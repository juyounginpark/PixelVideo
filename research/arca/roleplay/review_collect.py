import sys,json,time
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from crawl_arca import fetch
root=Path(__file__).parent
data=json.loads((root/'articles.json').read_text(encoding='utf-8'))
excluded={'185244234','183785098'}
for row in data['articles']:
    if row['id'] in excluded: continue
    path=root/(row['id']+'.html')
    try:
        if not path.exists():
            time.sleep(3)
            path.write_bytes(fetch(row['url']))
        soup=BeautifulSoup(path.read_bytes(),'html.parser')
        body=soup.select_one('.article-content')
        if body is None: raise ValueError('missing body')
        row['text']=body.get_text('\n',strip=True)
        row['images']=[n.get('data-original') or n.get('src') for n in body.select('img')]
        row['links']=[n.get('href') for n in body.select('a[href]')]
        row['media']=[str(n) for n in body.select('video,iframe,audio')]
        print(row['id'],row['title'],'\n',row['text'],'\nIMAGES',row['images'],'MEDIA',len(row['media']),flush=True)
    except Exception as e:
        print(type(e).__name__,str(e),flush=True)
        break
(root/'bodies.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
