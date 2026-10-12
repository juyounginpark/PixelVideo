"""Recover only the two user-supplied production specs from this session transcript."""
import json
from pathlib import Path
SESSION=Path('C:/Users/0620f/.codex/sessions/2026/10/11/rollout-2026-10-11T22-08-12-01a12b13-fb28-7252-895f-e277096e39de.jsonl')
ROOT=Path(__file__).resolve().parents[2]
targets={'# MINSU REELS ENGINE V2.0':'MINSU_V2_USER_SPEC.md','# MINSU REELS — BGM & SFX SYSTEM':'MINSU_BGM_SFX_USER_SPEC.md'}
found={}
for line in SESSION.open(encoding='utf-8'):
    try:data=json.loads(line)
    except json.JSONDecodeError:continue
    p=data.get('payload',{})
    if p.get('role')!='user':continue
    text='\n'.join(c.get('text','') for c in p.get('content',[]) if c.get('type') in ('input_text','text'))
    for marker,name in targets.items():
        if marker in text and len(text)>1000 and '<environment_context>' not in text:
            if name not in found or len(text)>len(found[name]):found[name]=text
if set(found)!=set(targets.values()):raise RuntimeError('Exact user spec messages not found')
for name,text in found.items():
    (ROOT/name).write_text(text+'\n',encoding='utf-8');print(name,len(text),'characters, user message only')
