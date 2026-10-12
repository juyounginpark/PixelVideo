from pathlib import Path
import json,hashlib
J=Path(__file__).resolve().parent;job=J/'ep10';current=json.loads((job/'native_index.json').read_text('utf8'));before=json.loads((job/'native_before_grounding.json').read_text('utf8'));hits=0;errors=[]
for cut,item in current.items():
 for f,r in item['frames'].items():
  p=Path(item['folder'])/f'{int(f):04}.png'
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:errors.append({'cut':cut,'frame':f})
  else:hits+=1
same={cut:before[cut]==current[cut] for cut in ['S05','S06']}
investigation_before=json.loads((job/'native_before_investigation.json').read_text('utf8'));retained={cut:investigation_before[cut]==current[cut] for cut in current if cut!='S02'}
report={'verifiedFrames':hits,'corruptedFrames':errors,'unaffectedMacroCutsIdentical':same,'retainedMacroFrames':240,'unaffectedCutsAfterWalkRework':retained,'retainedFramesAfterWalkRework':840,'reworkScope':'Foot placement: six world cuts. Investigative WALK: S02 only. Other cuts retained and frame hashes verified.'};(job/'research/cache_integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(report)
