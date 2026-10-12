"""Collect all accessible Reels, rank by one common count field, download top N."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from getpass import getpass
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlparse

import instaloader

ROOT = Path(__file__).resolve().parent
HANDLE = re.compile(r"[A-Za-z0-9_.]{1,30}\Z")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def valid_handle(value: str) -> str:
    value = value.removeprefix("@")
    if not HANDLE.fullmatch(value) or value in {".", ".."}:
        raise argparse.ArgumentTypeError(f"Invalid Instagram handle: {value}")
    return value.lower()


def reel_shortcode(value: str) -> str:
    parsed = urlparse(value)
    match = re.fullmatch(r"/reel/([A-Za-z0-9_-]+)/?", parsed.path)
    if parsed.scheme != "https" or parsed.netloc not in {"instagram.com", "www.instagram.com", "m.instagram.com"} or not match:
        raise argparse.ArgumentTypeError("Expected an HTTPS Instagram /reel/ URL")
    return match.group(1)


class StopOnRateLimit(instaloader.RateController):
    def handle_429(self, query_type: str) -> None:
        raise instaloader.AbortDownloadException("Instagram rate limit (429). Retry later.")


def make_loader() -> instaloader.Instaloader:
    return instaloader.Instaloader(
        quiet=True, sleep=True, request_timeout=20, max_connection_attempts=1,
        fatal_status_codes=[401, 403, 429], rate_controller=StopOnRateLimit,
        download_pictures=False, download_video_thumbnails=False,
    )


def authenticate(loader: instaloader.Instaloader, username: str) -> None:
    # Sessions stay outside this OneDrive project. Passwords are never persisted.
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    session = base / "PIXELvideo" / "instagram" / f"session-{username}"
    if session.exists():
        loader.load_session_from_file(username, str(session))
        if loader.test_login() != username:
            raise RuntimeError("Saved session expired. Use --fresh-login to sign in again.")
        print(f"Using saved session for @{username}", flush=True)
        return
    if not sys.stdin.isatty():
        raise RuntimeError("Login requires an interactive terminal. Run with --login YOUR_USERNAME.")
    password = getpass(f"Instagram password for @{username} (hidden): ")
    try:
        loader.login(username, password)
    except instaloader.TwoFactorAuthRequiredException:
        loader.two_factor_login(input("Two-factor authentication code: ").strip())
    finally:
        del password
    session.parent.mkdir(parents=True, exist_ok=True)
    loader.save_session_to_file(str(session))
    print("Login session saved locally.", flush=True)


def count_value(post: instaloader.Post, name: str) -> int | None:
    try:
        value = getattr(post, name)
    except (KeyError, AttributeError):
        return None
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def select_top(rows: list[dict], count: int, complete: bool, metric: str) -> tuple[list[dict], str | None, str]:
    """Never call partial scans or incomplete metrics an account-wide top N."""
    if not complete:
        return [], None, "incomplete_scan"
    if not rows:
        return [], None, "no_reels"
    choices = [metric] if metric != "auto" else ["video_play_count", "video_view_count"]
    chosen = next((key for key in choices if all(row.get(key) is not None for row in rows)), None)
    if chosen is None:
        return [], None, "missing_counts"
    ranked = sorted(rows, key=lambda row: (row[chosen], row["published_at"], row["shortcode"]), reverse=True)
    selected = [dict(row, rank=rank, ranking_value=row[chosen]) for rank, row in enumerate(ranked[:count], 1)]
    return selected, chosen, "ranked"


def is_mp4(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 16:
        return False
    with path.open("rb") as stream:
        return stream.read(12)[4:8] == b"ftyp"


def download_video(loader: instaloader.Instaloader, post: instaloader.Post, path: Path) -> str:
    if is_mp4(path):
        return "already_present"
    temporary = path.with_suffix(".mp4.part")
    url = post.video_url
    if not url:
        raise RuntimeError("Reel has no downloadable video URL.")
    with loader.context.get_raw(url) as response:
        response.raise_for_status()
        expected = response.headers.get("Content-Length")
        with temporary.open("wb") as stream:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    stream.write(chunk)
        if expected and temporary.stat().st_size != int(expected):
            raise RuntimeError("Incomplete download; partial file retained, not counted as downloaded.")
    if not is_mp4(temporary):
        raise RuntimeError("Response is not an MP4 video; partial file retained.")
    temporary.replace(path)
    return "downloaded"


def scan_account(loader: instaloader.Instaloader, handle: str, directory: Path, args: argparse.Namespace) -> dict:
    report = {
        "handle": handle, "profile_url": f"https://www.instagram.com/{handle}/",
        "started_at": now(), "scan_complete": False, "status": "scanning",
        "requested_count": args.count, "ranking_metric_requested": args.metric,
        "reels": [], "selected": [], "errors": [],
        "scope": "All Reels returned by Instagram to this session; unavailable/deleted Reels excluded.",
    }
    report_path = directory / "ranking.json"
    write_json(report_path, report)
    posts: dict[str, instaloader.Post] = {}
    try:
        profile = instaloader.Profile.from_username(loader.context, handle)
        for post in profile.get_reels():
            if post.shortcode in posts:
                continue
            if args.scan_limit is not None and len(posts) >= args.scan_limit:
                report["errors"].append("Scan limit reached; no account-wide ranking or downloads.")
                break
            if not post.is_video:
                raise RuntimeError("Unexpected non-video in Reels listing; scan cannot be certified.")
            posts[post.shortcode] = post
            row = {
                "shortcode": post.shortcode,
                "url": f"https://www.instagram.com/reel/{post.shortcode}/",
                "published_at": post.date_utc.replace(tzinfo=timezone.utc).isoformat(),
                "counts_collected_at": now(),
                "video_play_count": count_value(post, "video_play_count"),
                "video_view_count": count_value(post, "video_view_count"),
            }
            report["reels"].append(row)
            write_json(report_path, report)
            print(f"  @{handle}: scanned {len(posts)} Reels", flush=True)
            if args.delay:
                time.sleep(args.delay)
        else:
            report["scan_complete"] = True
    except KeyboardInterrupt:
        report["status"] = "interrupted"
        report["finished_at"] = now()
        write_json(report_path, report)
        raise
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["status"] = "scan_failed"
        report["finished_at"] = now()
        write_json(report_path, report)
        raise

    selected, metric, status = select_top(report["reels"], args.count, report["scan_complete"], args.metric)
    report.update(selected=selected, ranking_metric_used=metric, status=status)
    write_json(report_path, report)
    if status != "ranked":
        print(f"  @{handle}: {status}; no downloads.", flush=True)
    elif args.rank_only:
        report["status"] = "ranked_only"
    else:
        for row in selected:
            post = posts[row["shortcode"]]
            destination = directory / f"{row['shortcode']}.mp4"
            try:
                row["download_status"] = download_video(loader, post, destination)
                row["video_file"] = str(destination.resolve())
                metadata = dict(row, handle=handle, ranking_metric=metric, caption=post.caption)
                write_json(directory / f"{row['shortcode']}.json", metadata)
                (directory / f"{row['shortcode']}.txt").write_text(
                    f"{row['url']}\nPublished: {row['published_at']}\n"
                    f"Rank: {row['rank']} | {metric}: {row['ranking_value']}\n\n{post.caption or ''}\n",
                    encoding="utf-8",
                )
                print(f"  #{row['rank']} {row['ranking_value']:,}: {destination.name} ({row['download_status']})", flush=True)
            except KeyboardInterrupt:
                row["download_status"] = "interrupted"
                report["status"] = "interrupted"
                write_json(report_path, report)
                raise
            except Exception as exc:
                row["download_status"] = "failed"
                row["error"] = f"{type(exc).__name__}: {exc}"
                report["errors"].append(row["error"])
                if isinstance(exc, (instaloader.AbortDownloadException, instaloader.LoginRequiredException)):
                    report["status"] = "download_failed"
                    write_json(report_path, report)
                    raise
            write_json(report_path, report)
        report["status"] = "download_failed" if report["errors"] else "complete"
    report["finished_at"] = now()
    write_json(report_path, report)
    return report


def download_links(loader: instaloader.Instaloader, urls: list[str], output: Path) -> int:
    summary = {"started_at": now(), "selection": "user_provided_links", "reels": []}
    seen = set()
    exit_code = 0
    for index, supplied_url in enumerate(urls):
        code = reel_shortcode(supplied_url)
        if code in seen:
            continue
        seen.add(code)
        row = {
            "shortcode": code, "submitted_url": supplied_url,
            "url": f"https://www.instagram.com/reel/{code}/",
            "selection": "user_provided_link", "account_top_rank": None,
            "started_at": now(), "status": "fetching",
        }
        summary["reels"].append(row)
        record_path = output / "direct_links" / f"{code}.json"
        write_json(record_path, row)
        try:
            print(f"Downloading supplied Reel: {row['url']}", flush=True)
            # This route never enumerates profiles or their Reel lists.
            post = instaloader.Post.from_shortcode(loader.context, code)
            if not post.is_video:
                raise RuntimeError("Supplied post is not a video")
            handle = valid_handle(post.owner_username)
            directory = output / handle
            directory.mkdir(parents=True, exist_ok=True)
            row.update(
                handle=handle, published_at=post.date_utc.replace(tzinfo=timezone.utc).isoformat(),
                counts_collected_at=now(),
                video_play_count=count_value(post, "video_play_count"),
                video_view_count=count_value(post, "video_view_count"), caption=post.caption,
            )
            destination = directory / f"{code}.mp4"
            row["download_status"] = download_video(loader, post, destination)
            row.update(status="complete", video_file=str(destination.resolve()))
            write_json(directory / f"{code}.json", row)
            (directory / f"{code}.txt").write_text(f"{row['url']}\n\n{post.caption or ''}\n", encoding="utf-8")
            print(f"Saved: {destination}", flush=True)
        except KeyboardInterrupt:
            row["status"] = "interrupted"
            write_json(record_path, row)
            write_json(output / "direct_download_summary.json", summary)
            raise
        except Exception as exc:
            row.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            print(f"Failed: {row['error']}", file=sys.stderr, flush=True)
            exit_code = 1
            if isinstance(exc, (instaloader.AbortDownloadException, instaloader.LoginRequiredException)):
                summary["not_attempted_urls"] = urls[index + 1:]
                summary["stopped_reason"] = "Authentication/access/rate limit"
                break
        finally:
            row["finished_at"] = now()
            write_json(record_path, row)
            write_json(output / "direct_download_summary.json", summary)
    summary["finished_at"] = now()
    write_json(output / "direct_download_summary.json", summary)
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download each account's highest-viewed Reels (default: top 3).")
    targets = parser.add_mutually_exclusive_group()
    targets.add_argument("--accounts", nargs="+", type=valid_handle, help="Override accounts.json")
    targets.add_argument("--urls", nargs="+", help="Download supplied Reel links without profile enumeration")
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--output", type=Path, default=ROOT / "references")
    parser.add_argument("--login", type=valid_handle, help="Your Instagram username; password entered only in terminal")
    parser.add_argument("--fresh-login", action="store_true", help="Sign in again instead of loading saved session")
    parser.add_argument("--login-only", action="store_true")
    parser.add_argument("--rank-only", action="store_true", help="Collect rankings without downloading videos")
    parser.add_argument("--metric", choices=["auto", "video_play_count", "video_view_count"], default="auto")
    parser.add_argument("--scan-limit", type=int, help="Diagnostic cap; incomplete scans NEVER download top 3")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between Reel scans")
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.count < 1 or args.delay < 0 or (args.scan_limit is not None and args.scan_limit < 1):
        parser.error("--count/--scan-limit must be positive; --delay must be nonnegative")
    if (args.login_only or args.fresh_login) and not args.login:
        parser.error("--login-only/--fresh-login require --login")
    if args.urls:
        if args.rank_only:
            parser.error("--rank-only cannot be used with --urls; supplied links are not account rankings")
        for url in args.urls:
            try:
                reel_shortcode(url)
            except argparse.ArgumentTypeError as exc:
                parser.error(str(exc))
    handles = args.accounts or [valid_handle(v) for v in json.loads((ROOT / "accounts.json").read_text(encoding="utf-8"))]
    handles = list(dict.fromkeys(handles))
    loader = make_loader()
    try:
        if args.login:
            if args.fresh_login:
                # Move only the explicitly named session aside; retain it for recovery.
                base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
                session = base / "PIXELvideo" / "instagram" / f"session-{args.login}"
                if session.exists():
                    session.replace(session.with_name(session.name + f".backup-{time.time_ns()}"))
            authenticate(loader, args.login)
        if args.login_only:
            return 0
        output = args.output.resolve()
        if args.urls:
            return download_links(loader, args.urls, output)
        summary = {"started_at": now(), "count_per_account": args.count, "selection": "highest_count", "accounts": []}
        output.mkdir(parents=True, exist_ok=True)
        exit_code = 0
        for handle in handles:
            print(f"\nScanning all accessible Reels for @{handle}...", flush=True)
            try:
                report = scan_account(loader, handle, output / handle, args)
                summary["accounts"].append({
                    "handle": handle, "status": report["status"], "scanned": len(report["reels"]),
                    "selected": len(report["selected"]), "ranking_file": str(output / handle / "ranking.json"),
                })
                if report["status"] not in {"complete", "ranked_only", "no_reels"}:
                    exit_code = 1
            except Exception as exc:
                summary["accounts"].append({"handle": handle, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
                print(f"  Failed: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
                exit_code = 1
                if isinstance(exc, (instaloader.AbortDownloadException, instaloader.LoginRequiredException)):
                    summary["stopped_reason"] = "Authentication/access/rate limit; remaining accounts were not attempted."
                    summary["not_attempted"] = handles[len(summary["accounts"]):]
                    break
            finally:
                summary["updated_at"] = now()
                write_json(output / "download_summary.json", summary)
        print(f"\nResults: {output / 'download_summary.json'}", flush=True)
        if summary.get("stopped_reason"):
            print("If login is required, rerun with --login YOUR_USERNAME. If rate-limited, retry later.", flush=True)
        return exit_code
    except KeyboardInterrupt:
        print("\nStopped. Collected metadata and completed videos are retained.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        loader.close()


if __name__ == "__main__":
    raise SystemExit(main())
