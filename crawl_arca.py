"""Collect public Arca listing metadata; optionally fetch accessible article text."""
import argparse
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

DEFAULT_URL = 'https://arca.live/b/spooky?category=%ED%95%9C%EA%B5%AD%20%EA%B4%B4%EB%8B%B4&cut=50'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def extract_listing(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    seen = set()
    for row in soup.select('a.vrow[href]'):
        if any(c.startswith('notice') for c in row.get('class', [])):
            continue
        match = re.match(r'^/b/spooky/(\d+)(?:\?|$)', row['href'])
        title = row.select_one('.col-title .title')
        if not match or not title or match[1] in seen:
            continue
        seen.add(match[1])
        def value(selector):
            node = row.select_one(selector)
            return node.get_text(' ', strip=True) if node else None
        stamp = row.select_one('time[datetime]')
        result.append({
            'id': match[1], 'title': title.get_text(' ', strip=True),
            'url': f'https://arca.live/b/spooky/{match[1]}',
            'listing_category': value('.badge'),
            'published_at': stamp['datetime'] if stamp else None,
            'views_displayed': value('.col-view'),
            'rating_displayed': value('.col-rate'),
            'comments_displayed': value('.comment-count'),
            'body_status': 'not_requested',
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=DEFAULT_URL)
    parser.add_argument('--output', type=Path, default=Path('research/arca/collected'))
    parser.add_argument('--bodies', action='store_true')
    parser.add_argument('--limit', type=int, default=3, help='Maximum bodies, not listing rows')
    parser.add_argument('--delay', type=float, default=3)
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme != 'https' or parsed.hostname != 'arca.live' or parsed.path != '/b/spooky':
        parser.error('Use an HTTPS arca.live/b/spooky listing URL')
    if args.limit < 1 or args.delay < 1:
        parser.error('limit and delay must be at least 1')
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        html = fetch(args.url)
    except urllib.error.HTTPError as error:
        print(f'Listing HTTP {error.code}; stopped without retry.')
        return 1
    (args.output / 'listing.html').write_bytes(html)
    rows = extract_listing(html)
    if not rows:
        print('No article rows found. Check listing.html; no bodies requested.')
    if args.bodies:
        for row in rows[:args.limit]:
            time.sleep(args.delay)
            try:
                body_html = fetch(row['url'])
                soup = BeautifulSoup(body_html, 'html.parser')
                body = soup.select_one('.article-content')
                if body is None:
                    row['body_status'] = 'content_not_found'
                    break
                for node in body.select('script, style'):
                    node.decompose()
                images = [urljoin(row['url'], n.get('src', '')) for n in body.select('img[src]')]
                text = body.get_text('\n', strip=True)
                row.update(body_status='collected', text=text, image_urls=images)
                (args.output / f"{row['id']}.html").write_bytes(body_html)
                (args.output / f"{row['id']}.md").write_text(
                    f"# {row['title']}\n\n원문: {row['url']}\n\n{text}\n", encoding='utf-8')
            except urllib.error.HTTPError as error:
                row['body_status'] = f'http_{error.code}'
                print(f'Article HTTP {error.code}; stopped without retry.')
                break
            except (OSError, TimeoutError) as error:
                row['body_status'] = 'network_error'
                print(f'Network error: {type(error).__name__}; stopped.')
                break
    result = {'source_url': args.url, 'collected_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'one listing page, notices excluded; no overall ranking claim', 'articles': rows}
    (args.output / 'articles.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 한국 괴담 목록 수집', '', f'목록 원문: {args.url}', '',
             '공지 제외, 한 페이지에서 확인한 목록. 실화 여부 및 원저작자 미검증.', '']
    lines.extend(f"- [{r['title']}]({r['url']}) · 본문 상태: {r['body_status']}" for r in rows)
    (args.output / 'INDEX.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Listing articles: {len(rows)}; bodies collected: {sum(r["body_status"] == "collected" for r in rows)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
