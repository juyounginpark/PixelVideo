"""Untrack generated artifacts only. No files are deleted from the workspace."""
from pathlib import Path
import subprocess,json
from datetime import datetime,timezone,timedelta
J=Path(__file__).resolve().parent;ROOT=J.parents[1]
top=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip()).resolve()
if top!=ROOT.resolve():raise ValueError('Unexpected Git root; refuse index cleanup')
patterns=['production/**/cache/**','production/**/frames/**','production/**/native/**','production/**/ui/**','exports/*.mp4','exports/*.mov','exports/*.mkv','exports/*.wav','production/**/silent*.mp4','production/**/preview*.mp4','production/**/bgm.wav','production/**/sfx.wav','production/**/mix.wav','production/**/mix_raw.wav','production/**/mix_normalized.wav','*.log']
raw=subprocess.check_output(['git','ls-files','-z','--',*patterns],cwd=ROOT);names=[x.decode('utf8') for x in raw.split(b'\0') if x]
for name in names:
 if not (ROOT/name).resolve().is_relative_to(ROOT.resolve()):raise ValueError('Path outside workspace')
 if name.startswith('research/') or '/fonts/' in name or name.endswith('episode.json'):raise ValueError('Protected source selected')
before={n:(ROOT/n).exists() for n in names};pathspec=J/'review/gitignore_paths.tmp';pathspec.write_bytes(raw)
try:
 if names:
  result=subprocess.run(['git','rm','--cached','--quiet','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul'],cwd=ROOT,capture_output=True,text=True,encoding='utf8',errors='replace')
  if result.returncode:raise RuntimeError(result.stderr)
finally:pathspec.unlink(missing_ok=True)
remaining=subprocess.check_output(['git','ls-files','-z','--',*patterns],cwd=ROOT);lost=[n for n,existed in before.items() if existed and not (ROOT/n).exists()]
report={'untrackedGeneratedFiles':len(names),'remainingTrackedGeneratedPaths':len([x for x in remaining.split(b'\0') if x]),'localFilesLost':lost,'method':'git rm --cached with literal NUL-separated scoped paths; no filesystem deletion','gitRoot':str(top)}
(J/'review/gitignore_cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
with (ROOT/'PROMPT_LOG.md').open('a',encoding='utf8') as f:f.write('\nU-098 실행 보완 — '+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n새 제외 규칙에 해당하는 기존 Git 추적 생성물 '+str(len(names))+'개를 확인했다. .gitignore의 실제 효과를 위해 해당 생성물만 git rm --cached로 추적 해제. 로컬 파일·기존 커밋 이력·소재·폰트·재사용 음원·QA 보고서 유지. 앞선 "추적 해제 미실시" 메모 이후 수행한 추가 조치다. 커밋은 수행하지 않았다.\n')
print(json.dumps(report))
if lost:raise SystemExit('Unexpected filesystem loss')
