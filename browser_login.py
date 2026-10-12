"""User-controlled Instagram browser login; transfer only Instagram cookies locally."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

from playwright.sync_api import sync_playwright

from download_reels import make_loader, valid_handle, write_json


def instagram_cookies(cookies: list[dict]) -> dict[str, str]:
    return {
        item["name"]: item["value"] for item in cookies
        if item["domain"].lstrip(".") == "instagram.com"
        and (item.get("expires", -1) == -1 or item["expires"] > time.time())
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign in directly in an Instagram browser window.")
    parser.add_argument("--browser", choices=["msedge", "chrome"], default="msedge")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "PIXELvideo" / "instagram"
    base.mkdir(parents=True, exist_ok=True)
    ui = tk.Tk()
    ui.withdraw()
    ui.attributes("-topmost", True)
    try:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(base / f"browser-profile-{args.browser}"),
                channel=args.browser, headless=False,
                viewport=None,
            )
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
                write_json(base / "browser_login_status.json", {"status": "waiting_for_browser_login"})
                print("Sign in directly in the browser. No password is read by this program.", flush=True)
                deadline = time.monotonic() + args.timeout
                cookies = {}
                while time.monotonic() < deadline:
                    cookies = instagram_cookies(context.cookies("https://www.instagram.com/"))
                    blocked_page = any(word in page.url for word in ("/challenge/", "/checkpoint/", "/accounts/login"))
                    if all(cookies.get(key) for key in ("sessionid", "csrftoken", "ds_user_id")) and not blocked_page:
                        break
                    page.wait_for_timeout(1000)
                else:
                    messagebox.showerror("PIXELvideo", "로그인이 확인되지 않았습니다. 인스타그램 인증을 완료한 뒤 다시 실행하세요.", parent=ui)
                    return 1
                while True:
                    supplied = simpledialog.askstring(
                        "PIXELvideo", "브라우저에서 로그인한 인스타그램 아이디를 입력하세요.\n(이메일·비밀번호가 아닌 @사용자명)", parent=ui,
                    )
                    if supplied is None:
                        return 1
                    try:
                        username = valid_handle(supplied.strip())
                        break
                    except argparse.ArgumentTypeError:
                        messagebox.showerror("PIXELvideo", "올바른 인스타그램 아이디를 입력하세요.", parent=ui)
                loader = make_loader()
                try:
                    loader.load_session(username, cookies)
                    loader.save_session_to_file(str(base / f"session-{username}"))
                finally:
                    loader.close()
                write_json(base / "login.json", {
                    "username": username, "signed_in_at": datetime.now(timezone.utc).isoformat(),
                    "method": "dedicated_browser", "api_session_verified": False,
                })
                write_json(base / "browser_login_status.json", {"status": "session_saved", "api_session_verified": False})
                messagebox.showinfo(
                    "PIXELvideo", "브라우저 로그인 세션을 저장했습니다.\n다음 다운로드 실행 시 이 세션을 사용합니다.\nAPI 접근 및 429 해제 여부는 아직 확인하지 않았습니다.", parent=ui,
                )
                return 0
            finally:
                context.close()
    except Exception as exc:
        # Do not print cookies, session contents, passwords, or browser page content.
        write_json(base / "browser_login_status.json", {"status": "failed", "error_type": type(exc).__name__})
        messagebox.showerror(
            "PIXELvideo", f"브라우저 로그인을 완료하지 못했습니다 ({type(exc).__name__}).\n브라우저를 직접 닫았거나 실행이 차단되었을 수 있습니다.\n인스타그램 인증 상태를 확인한 뒤 다시 시도하세요.", parent=ui,
        )
        return 1
    finally:
        ui.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
