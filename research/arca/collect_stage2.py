import json
import sys
import time
import urllib.error
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from crawl_arca import fetch
from bs4 import BeautifulSoup

root = Path('research/arca')
out = root / 'stage2'
out.mkdir(parents=True, exist_ok=True)
source = json.loads((root / 'collected/articles.json').read_text(encoding='utf-8'))
stage1 = {row[0]: row for row in json.loads((root / 'stage1.json').read_text(encoding='utf-8'))}
results = []
for row in source['articles']:
    if stage1[row['id']][1] == '제외':
        continue
    cached = out / f"{row['id']}.html"
    if not cached.exists():
        cached = root / 'collected' / f"{row['id']}.html"
    try:
        if cached.exists():
            raw = cached.read_bytes()
        else:
            time.sleep(3)
            raw = fetch(row['url'])
        (out / f"{row['id']}.html").write_bytes(raw)
        soup = BeautifulSoup(raw, 'html.parser')
        body = soup.select_one('.article-content')
        if body is None:
            results.append(dict(row, stage2_status='content_not_found'))
            continue
        for node in body.select('script,style'):
            node.decompose()
        blocks = []
        for p in body.select('p, h1, h2, h3, li, blockquote'):
            if p.find_parent(['p','li','blockquote']):
                continue
            text = p.get_text(' ', strip=True)
            if text:
                blocks.append({'number':len(blocks)+1, 'text':text})
        if not blocks:
            blocks = [{'number':1,'text':body.get_text(' ',strip=True)}]
        images = [{'number':i,'url':urljoin(row['url'],n.get('src',''))} for i,n in enumerate(body.select('img[src]'),1)]
        links = [{'text':n.get_text(' ',strip=True), 'url':urljoin(row['url'],n['href'])} for n in body.select('a[href]')]
        media = [str(n) for n in body.select('iframe,video,audio')]
        result = dict(row, stage2_status='collected', blocks=blocks, images=images, links=links, embedded_media=media)
        results.append(result)
        (out / f"{row['id']}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        (out / f"{row['id']}.md").write_text(f"# {row['title']}\n\n{row['url']}\n\n"+'\n\n'.join(f"P{b['number']}: {b['text']}" for b in blocks),encoding='utf-8')
        print(row['id'], 'blocks',len(blocks),'images',len(images),'embedded',len(media),flush=True)
    except urllib.error.HTTPError as error:
        results.append(dict(row,stage2_status=f'http_{error.code}'))
        print(row['id'],'HTTP',error.code,'stopped',flush=True)
        break
    except (OSError,TimeoutError) as error:
        results.append(dict(row,stage2_status='network_error'))
        print(row['id'],type(error).__name__,'stopped',flush=True)
        break
(out / 'articles.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
