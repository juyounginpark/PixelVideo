"""One-time evidence inventory; never selects or mutates the topic supply."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    R.joinpath('review').mkdir(exist_ok=True)
    files=[p for folder in ('research/namuwiki','prompts','exports') for p in (ROOT/folder).rglob('*') if p.is_file()]
    target=R/'review/preservation_before.json'
    if not target.exists():target.write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in files},ensure_ascii=False,indent=2),'utf-8')
    log=ROOT/'PROMPT_LOG.md'
    if '# U-088' not in log.read_text('utf-8'):
        with log.open('ab') as f:f.write(b'\n\n'+(ROOT/'MINSU_V4_USER_SPEC.md').read_bytes())
    print('V4 request recorded; supply and previous outputs inventoried',len(files))
