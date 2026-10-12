import json
import sys
import urllib.error
from datetime import datetime,timezone
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from crawl_arca import fetch,extract_listing,DEFAULT_URL

root=Path('research/arca')
original=json.loads((root/'collected/articles.json').read_text(encoding='utf-8'))
record={'source_url':DEFAULT_URL,'status':'not_measured','articles':[]}
try:
 raw=fetch(DEFAULT_URL)
 now=datetime.now(timezone.utc)
 (root/'listing_reselection.html').write_bytes(raw)
 current={r['id']:r for r in extract_listing(raw)}
 record.update(status='measured',collected_at_utc=now.isoformat())
 for old in original['articles']:
  row=current.get(old['id'])
  if row is None:
   record['articles'].append({'id':old['id'],'status':'not_in_current_page'})
   continue
  count=(row.get('views_displayed') or '').replace(',','')
  published=datetime.fromisoformat(row['published_at'].replace('Z','+00:00')) if row.get('published_at') else None
  hours=(now-published).total_seconds()/3600 if published and published.tzinfo else None
  views=int(count) if count.isdigit() else None
  record['articles'].append(dict(row,status='measured',collected_at_utc=now.isoformat(),views=views,elapsed_hours=hours,
     lifetime_avg_views_per_hour=views/hours if views is not None and hours and hours>0 else None,
     interval_views_per_hour=None))
 print('Fresh listing rows matched:',sum(r['status']=='measured' for r in record['articles']))
except urllib.error.HTTPError as error:
 record.update(status=f'http_{error.code}',attempted_at_utc=datetime.now(timezone.utc).isoformat())
 print('Listing HTTP',error.code,'stopped without retry')
(root/'reselection_metrics.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
