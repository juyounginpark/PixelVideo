from pathlib import Path
import re,json
J=Path(__file__).resolve().parent;rows=[]
for p in [J/'sample_render.log',J/'sample_rework.log',J/'ep10/stills.log',J/'ep10/stills_rework.log',J/'ep10/full_render.log',J/'ep10/full_render_rework.log',J/'ep10/grounding_render.log',J/'ep10/investigation_rework.log']:
 if not p.exists():continue
 raw=p.read_bytes();text=raw.decode('utf16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf8',errors='replace');times=re.findall(r'(\d+):(\d+\.\d+)\s+render\s+\| Saved:',text)
 rows.append({'log':str(p.relative_to(J)),'savedFrames':len(times),'lastSavedElapsedSeconds':int(times[-1][0])*60+float(times[-1][1]) if times else None,'measurement':'Last saved-frame elapsed time from Blender log; not total process wall time'})
(J/'review/render_phases.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows))
