"""Preserve a challenge response; use bounded accessible primary-source records."""
from pathlib import Path
import sys,requests
from bs4 import BeautifulSoup
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT
folder=J/'research';ledger=read(folder/'claim_ledger.json');blocked=folder/'study2023.html';challenge=folder/'study2023_challenge.html'
if challenge.exists() or blocked.exists() and 'Checking your browser' in blocked.read_text('utf-8',errors='replace'):
 if blocked.exists() and not challenge.exists():blocked.rename(challenge)
 record={'id':'study2023','url':'https://www.bristol.ac.uk/news/2023/february/zebra-stripes.html','type':'Researchers university primary announcement with publication link','browserVerifiedArticle':'https://pmc.ncbi.nlm.nih.gov/articles/PMC10088525/','articleDOI':'10.1242/jeb.244778'}
 p=folder/'study2023_verified.html'
 if not p.exists():
  r=requests.get(record['url'],timeout=45);r.raise_for_status();p.write_bytes(r.content)
 text=BeautifulSoup(p.read_text('utf-8',errors='replace'),'html.parser').get_text(' ',strip=True)
 if 'contrast' not in text.lower() or 'Caro' not in text:raise ValueError('No research evidence in alternate source')
 record.update(snapshot=str(p.relative_to(ROOT)),sha256=sha(p));ledger['sources']=[record if s['id']=='study2023' else s for s in ledger['sources']]
 pdf=folder/'study2020.pdf';url='https://research-information.bris.ac.uk/ws/portalfiles/portal/246843415/rspb.2020.1521.pdf'
 if not pdf.exists():
  r=requests.get(url,timeout=45);r.raise_for_status()
  if not r.content.startswith(b'%PDF'):raise ValueError('Non-PDF research response')
  pdf.write_bytes(r.content)
 from pypdf import PdfReader
 document=PdfReader(pdf);text='\n'.join(page.extract_text() for page in document.pages);(folder/'study2020.txt').write_text(text,'utf-8')
 if 'check' not in text.lower() or 'land' not in text.lower():raise ValueError('Expected checked-coat results missing')
 if not any(s['id']=='study2020' for s in ledger['sources']):ledger['sources'].append({'id':'study2020','url':url,'snapshot':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'articleDOI':'10.1098/rspb.2020.1521','type':'published paper in authors institutional repository'})
 for claim in ledger['claims']:
  if claim['id']=='C3':claim['source']='study2020';claim['location']='Abstract and results comparing striped, checked and grey coats'
 ledger['retrievalLimits']={'challengeResponse':str(challenge.relative_to(ROOT)),'status':'HTTP200 challenge was not treated as article evidence','noRepeatedChallengeRequests':True,'sourceAlternatives':'public researchers university announcement and institutional published paper; no restriction bypass'}
 write(folder/'claim_ledger.json',ledger)
print('Primary evidence repaired; challenge response preserved')
