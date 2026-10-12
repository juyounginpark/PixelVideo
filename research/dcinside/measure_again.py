import json
import sys
from datetime import datetime,timezone
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from crawl_arca import fetch
root=Path('research/dcinside')
baseline=json.loads((root/'sample20.json').read_text(encoding='utf-8'))
access=json.loads((root/'access.json').read_text(encoding='utf-8'))
raw=fetch(access['url'])
second=datetime.now(timezone.utc)
(root/'listing_second.html').write_bytes(raw)
observations={}
for row in BeautifulSoup(raw,'html.parser').select('tr.us-post[data-no]'):
    count=row.select_one('.gall_count').get_text(strip=True).replace(',','')
    if count.isdigit():observations[row['data-no']]=int(count)
for item in baseline:
    t1=datetime.fromisoformat(item['collected_at_utc'])
    duration=(second-t1).total_seconds()/3600
    v2=observations.get(item['no'])
    delta=v2-item['views'] if v2 is not None and item['views'] is not None else None
    item.update(second_collected_at_utc=second.isoformat(),second_views=v2,
        interval_hours=duration,view_delta=delta,
        interval_views_per_hour=delta/duration if delta is not None and delta>=0 and duration>0 else None,
        interval_status='measured_short_interval' if delta is not None and delta>=0 else 'missing_or_invalid')
(root/'sample20.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'snapshots.json').write_text(json.dumps({'first':access['collected_at_utc'],'second':second.isoformat(),
   'interval_hours':duration,'short_interval_only':True,'own_body_requests_may_affect_views':True},indent=2),encoding='utf-8')
print('Interval minutes:',round(duration*60,2))
for item in baseline:print(item['no'],item['views'],item['second_views'],item['view_delta'],round(item['interval_views_per_hour'],2) if item['interval_views_per_hour'] is not None else None)
