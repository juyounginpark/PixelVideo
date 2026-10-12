from pathlib import Path
import json
J=Path(__file__).resolve().parent;job=J/'ep10';qa_path=job/'review/final/technical_qa.json';qa=json.loads(qa_path.read_text('utf8'));geometry=json.loads((job/'research/geometry_qa.json').read_text('utf8'));cache=json.loads((job/'research/cache_integrity.json').read_text('utf8'));rules=json.loads((J/'QA_RULES.json').read_text('utf8'))['technical'];errors=[]
for locale in ['ko','en']:
 if locale not in qa:errors.append(locale+' missing');continue
 r=qa[locale]
 if not r['decodePassed'] or not r['formatPassed'] or r['uiFrames']!=960:errors.append(locale+' media failure')
 if r.get('decodedFrameCount')!=960:errors.append(locale+' decoded frame count')
 if r['glyphFallbacks'] or r['textCollisions'] or r['cupOutOfFrame'] or not r['audioPeakPassed']:errors.append(locale+' typography/framing/audio failure')
if geometry['invalidMeshes'] or geometry['degenerateNormals'] or not all(geometry['continuity'].values()):errors.append('Geometry/continuity failure')
if any(abs(r['bootMinimumZ'])>rules['groundTolerance'] for r in geometry['samples']):errors.append('Grounding failure')
if cache['corruptedFrames'] or cache['verifiedFrames']!=960:errors.append('Native cache failure')
if qa['preservation']['changedFiles']:errors.append('Original source/export changed')
qa['gate']={'technicalPassed':not errors,'errors':errors,'editorialAutoApproved':False,'rulesVersion':'6.0.0'};qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(qa['gate'])
if errors:raise SystemExit(1)
