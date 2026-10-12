import json
import sys
import time
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from crawl_arca import fetch

root=Path('research/dcinside')
access=json.loads((root/'access.json').read_text(encoding='utf-8'))
observed=datetime.fromisoformat(access['collected_at_utc'])
soup=BeautifulSoup((root/'listing.html').read_bytes(),'html.parser')
articles=[]
title_excluded={'82239':'일부혐주의 경고: 높은 수위 우려로 제목 단계 제외',
                '80597':'실존 인물의 실제 경험·화제 중심 제목',
                '79697':'실제 참사에 관한 제목'}
for row in soup.select('tr.us-post[data-no]'):
    if row.select_one('.gall_subject').get_text(strip=True) == '공지':
        continue
    a=row.select_one('.gall_tit a[href]')
    if not a:
        continue
    no=row['data-no']
    date=row.select_one('.gall_date').get('title')
    count=row.select_one('.gall_count').get_text(strip=True).replace(',','')
    published=datetime.strptime(date,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone(timedelta(hours=9))) if date else None
    hours=(observed-published).total_seconds()/3600 if published else None
    views=int(count) if count.isdigit() else None
    item={'no':no,'title':a.get_text(' ',strip=True),'url':urljoin('https://gall.dcinside.com',a['href']),
          'published_at_kst':published.isoformat() if published else None,'collected_at_utc':observed.isoformat(),
          'timezone_assumption':'DC display interpreted as Asia/Seoul',
          'views':views,'recommendations':row.select_one('.gall_recommend').get_text(strip=True),
          'elapsed_hours':hours,'lifetime_avg_views_per_hour':views/hours if views is not None and hours and hours>0 else None,
          'interval_views_per_hour':None,
          'stage1':'제외' if no in title_excluded else '통과',
          'stage1_reason':title_excluded.get(no,'유실·발굴·작품 소개 단서 또는 모호한 제목: 본문 확인 필요'),
          'body_status':'not_requested'}
    articles.append(item)
    if len(articles)==20:break
(root/'sample20.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2),encoding='utf-8')
body_dir=root/'bodies';body_dir.mkdir(exist_ok=True)
for item in articles:
    if item['stage1']=='제외':continue
    try:
        target=body_dir/f"{item['no']}.html"
        if target.exists():raw=target.read_bytes()
        else:
            time.sleep(3)
            raw=fetch(item['url'])
            target.write_bytes(raw)
        page=BeautifulSoup(raw,'html.parser')
        body=page.select_one('.write_div')
        if body is None:
            item['body_status']='content_not_found'
            continue
        blocks=[]
        for tag in body.select('p,h1,h2,h3,li,blockquote'):
            if tag.find_parent(['p','li','blockquote']):continue
            text=tag.get_text(' ',strip=True)
            if text:blocks.append({'number':len(blocks)+1,'text':text})
        if not blocks:blocks=[{'number':1,'text':body.get_text(' ',strip=True)}]
        item.update(body_status='collected',blocks=blocks,
            images=[{'number':i,'url':urljoin(item['url'],n.get('data-original') or n['src']), 'lazy':bool(n.get('data-original'))} for i,n in enumerate(body.select('img[src]'),1)],
            links=[{'text':n.get_text(' ',strip=True),'url':urljoin(item['url'],n['href'])} for n in body.select('a[href]')],
            media=[str(n) for n in body.select('iframe,video,audio')],
            body_collected_at_utc=datetime.now(timezone.utc).isoformat())
        (body_dir/f"{item['no']}.md").write_text(f"# {item['title']}\n\n{item['url']}\n\n"+'\n\n'.join(f"P{b['number']}: {b['text']}" for b in blocks),encoding='utf-8')
        print(item['no'],'blocks',len(blocks),'images',len(item['images']),'media',len(item['media']),flush=True)
    except urllib.error.HTTPError as error:
        item['body_status']=f'http_{error.code}'
        print('HTTP',error.code,'stopped',flush=True)
        break
    except (OSError,TimeoutError) as error:
        item['body_status']='network_error'
        print(type(error).__name__,'stopped',flush=True)
        break
    finally:
        (root/'sample20.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2),encoding='utf-8')
