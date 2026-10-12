from pathlib import Path
import json,hashlib
from datetime import datetime,timezone,timedelta
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def now():return datetime.now(timezone(timedelta(hours=9),'Asia/Seoul')).isoformat(timespec='seconds')
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for folder in ('config','review','ep08','cache','research'):(R/folder).mkdir(exist_ok=True)
log=ROOT/'PROMPT_LOG.md';text=log.read_text('utf-8')
if '## U-090 ' not in text:
 with log.open('a',encoding='utf-8') as f:
  f.write('\n\n## U-090 — MINSU V5 전면 재설계\n'+now()+' 원문:\n\n'+(ROOT/'MINSU_V5_USER_SPEC.md').read_text('utf-8'))
  f.write('''\n\n## P-042 — V5 소재·이야기·미술 재설계 v1\n'''+now()+''' 실행 전 기록. 도구 Blender/Pillow/FFmpeg, 추가 외부 LLM API 없음. EP07 실제 MP4와 ref3/ref4를 재추출해 컷별 사건·정보·반복·감정·가독성을 비교한다. 기존 나무위키 HTML/TXT 캐시와 공급 메타데이터를 보존하며 30~50개 후보를 근거 위치와 함께 추출한다. 접근 실패와 정책 미확인을 기록하고 자동 크롤링은 진행하지 않는다. 규칙 기반 제외→10개 상세 검토→5개 시각 후킹→독립 출처와 관심 점수→1개 선택의 근거를 남긴다. 점수와 흥행 성과는 구분한다. 실제 사건을 첫 프레임에 보여줄 수 있고 중간 증거와 마지막 보상이 있는 소재만 택한다. 검증 상태별 Story Map과 6단계 제작 게이트를 구현한다. 밝고 따뜻한 복셀 세계, 실제 전신 행동, 정면/측면/3/4 모델 검수, 한국어 단독/영어 별도 출력, 폰트 아틀라스와 텍스트 캐시를 사용한다. 동일 장면에서 CRT 미적용/레퍼런스 지향/모바일 지향 및 6/10/14% 강도를 비교한다. 사건에 맞춰 음악 강약과 SFX를 설계한다. 3~5초 미술 샘플→실제 프레임 검토→전체 저해상도 프리뷰→문제 컷 수정→최종1080 출력·분리 QA. 숫자로 재미를 인증하지 않으며 실시간 재생·청취·시청자 테스트의 수행 여부를 구분한다.\n''')
agents=ROOT/'AGENTS.md';a=agents.read_text('utf-8')
if 'U-090 / V5' not in a:
 a=a.replace('# PIXELvideo 작업 규칙','# PIXELvideo 작업 규칙\n\n## 최신 우선 지시 — U-090 / V5\n\n- MINSU_V5_USER_SPEC.md를 현재 단일 제작 기준으로 적용한다. 기존 공급 기록을 보존하며 지정 나무위키 분류 캐시의 후보 수집·선별 기능을 확장한다. 제한 우회 금지, 독립 사실 확인 필수.\n- 한국어 기본판과 영어 별도판을 출력한다. U-089의 동시 이중 자막은 V5에서 변경됐다. TTS 없음, 기존 BGM/SFX를 사건 강약에 맞춰 재사용한다.\n- 소재/이야기/콘티/미술/편집/최종 QA 6게이트. ref4의 밝은 복셀 인물·전신 행동 우선, ref3의 정보창과 CRT 문법 보완. 코드 실행이나 점수로 미적 합격을 선언하지 않는다.\n',1);agents.write_text(a,'utf-8')
paths=list((ROOT/'research/namuwiki').rglob('*'))+list((ROOT/'exports').glob('*.mp4'))+[ROOT/'prompts/MYSTERY_100_v1.md']
baseline=R/'review/preservation_before.json'
if not baseline.exists():write(baseline,{str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()})
write(R/'research/access.json',dict(checkedAt=now(),source='https://namu.wiki/w/미스터리%20관련%20정보',attempts=[dict(url=u,result='web tool non-retryable access error') for u in ['https://namu.wiki/robots.txt','https://namu.wiki/w/미스터리%20관련%20정보','https://namu.wiki/Policy']],policyVerified=False,action='Use existing local HTML/TXT snapshots; no crawler, bypass or repeated requests',mirrorUsed=False))
print('V5 request recorded; source baseline preserved')
