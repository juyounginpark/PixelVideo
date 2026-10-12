from pathlib import Path
import json,hashlib,re,html,subprocess
from imageio_ffmpeg import get_ffmpeg_exe
from PIL import Image,ImageDraw
J=Path(__file__).resolve().parent;ROOT=J.parents[1];job=J/'ep10';out=job/'review/final'
spec=json.loads((job/'episode.json').read_text('utf8'));topic=json.loads((job/'topic.json').read_text('utf8'));metrics=json.loads((job/('render_initial.json' if (job/'render_initial.json').exists() else 'render_metrics.json')).read_text('utf8'));qa=json.loads((out/'technical_qa.json').read_text('utf8'))
for locale in ['ko','en']:
 def tc(t):
  ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
 lines=['\n'.join([str(i+1),tc(c['start'])+' --> '+tc(c['end']),*c['lines']]) for i,c in enumerate(spec['captions'][locale])]
 (ROOT/'exports'/f'MINSU_EP10_V6.{locale}.srt').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
subprocess.run([get_ffmpeg_exe(),'-v','error','-ss','22','-i',str(ROOT/'exports/MINSU_EP10_V6_LYCURGUS_KO.mp4'),'-frames:v','1','-y',str(out/'ko_22.00.png')],check=True)
comparison=Image.new('RGB',(900,430),'#182031');draw=ImageDraw.Draw(comparison)
paths=[J.parent/'minsu_v5/review/media/ref4_02.00.png',J/'review/ep09_002.0.png',out/'ko_02.00.png',out/'ko_22.00.png']
for i,(p,label) in enumerate(zip(paths,['REFERENCE 4: 2s','EP09: 2s','EP10 V6: 2s','EP10: light paths'])):
 if p.exists():
  im=Image.open(p);im.thumbnail((225,600));comparison.paste(im,(i*225,30))
 draw.text((i*225+5,5),label,fill='white')
comparison.save(out/'reference_comparison.jpg')
report='''# V6 EP10 실제 결과 검수

선정 소재: 리쿠르고스의 컵. 기존 나무위키 자연과학 캐시에서 선정, 중복 검사. 제작 전 검토 92/100은 대중 반응 측정값이 아니다.

기: 같은 잔을 비추는 조명 이동으로 녹색→붉은색. 승: 같은 잔과 앞/뒤 조명 조건 확인. 전: 같은 유리 벽을 확대해 금·은 나노입자와 반사/투과 경로 설명. 결: 같은 장소·잔·조명 상태로 돌아와 첫 동작을 재확인.

핵심 수정: 상시 제목·챕터·번호·출처·프레임 제거. 전체 3D 사건 우선. 컷 독립 자막, 읽기 시간, 4프레임 등장, 이어지는 구절 유지. 설명 진입/복귀 계약. 사건 프레임에 카메라·픽셀 강조·SFX 연결. KO/EN 별도 출력. 실제 540×960→nearest 2배→1080 UI→고정 4픽셀 주기 6% 스캔라인. 제한된 명암·텍스처와 약한 ordered dither.

과학 근거: https://www.beilstein-journals.org/bjnano/articles/11/2 (doi:10.3762/bjnano.11.2). 같은 쪽 조명/관찰에서 반사색, 반대쪽에서 투과색; 금·은 나노입자의 광학 성질. 실제 색은 광원 스펙트럼과 관찰 조건에도 의존한다. '2020년 최초 원리 규명'과 제작자 의도 확정은 사용하지 않았다.

시청 경험 판단은 실제 출력 프레임·전환 부근 연속 프레임·전체 디코드를 근거로 한 제작자 검토다. 실시간 재생/청취와 대중 시청자 테스트를 수행한 것으로 표현하지 않는다.

처음 이탈하고 싶어질 수 있는 시점: 약 4–8초. 첫 색 변화 후 잔을 다시 확인하는 장면은 후킹보다 정보 증가 속도가 느리다. 이전 EP09의 고정 패널 반복은 제거했지만, 실제 관객의 흥미 유지까지 확인한 것은 아니다.
삭제한 UI/문구: 고정 대제목, 챕터/진행 번호, 상시 연구 연도, 반복 출처, 중복 오브젝트 상태창.
삭제·수정할 후보: 4–8초 재확인 동작의 일부를 줄일 여지가 있다. 막연한 '상호작용'은 '빛을 흩뜨리고 흡수한다'와 색마다 다른 반사/투과 설명으로 수정했다. 움직이는 빛 경로가 이를 보완하지만 실제 파장별 산란·흡수량을 재현한 것은 아니다.
다시 연출한 핵심 사건: 첫 색 변화와 SFX 0.8초 동기화, 불연속 엔딩 조명 왕복 수정, 설명 전 표면 접근/설명 후 카메라 복귀, 잘린 민수 구도 수정, 앞/뒤 조건과 자막 시간 일치.
남은 미술 한계: 잔 장식은 실제 유물의 정확한 복제보다 단순하다. 캐릭터 시선·손과 조명의 접촉은 추가적인 미세 연기 개선 여지가 있다. 레퍼런스 수준의 상업 미술/편집 완성도를 달성했다고 승인하지 않는다.
사실 전달의 한계: 색상은 실제 광학 계산이 아닌 조건에 연결된 설명용 애니메이션. 광자·입자 크기와 경로는 모식도이며 물리적 크기 비율/측정 데이터가 아니다. 고대 재료 미세구조를 순수 금/은 두 종류의 독립 입자로 정확하게 복제했다고 주장하지 않는다.
오디오 한계: 로컬 음악·효과음의 이벤트 시간, 음량, 피크, AAC는 분석했으나 음악적 자연스러움을 청취 승인하지 않았다.

기술 정상 작동과 '재미있다'는 판정은 구분한다. 완성 영상 파일은 제작 결과물이며 실제 대중 유지율을 보증하지 않는다.
'''
(out/'EDITORIAL_QA.md').write_text(report,encoding='utf8')
grounding=json.loads((job/'render_grounding.json').read_text('utf8')) if (job/'render_grounding.json').exists() else {};cache=json.loads((job/'render_cache_verification.json').read_text('utf8')) if (job/'render_cache_verification.json').exists() else {};phases=json.loads((J/'review/render_phases.json').read_text('utf8'))
investigation=json.loads((job/'render_investigation.json').read_text('utf8'));active_native_seconds=metrics['wallSeconds']+grounding['wallSeconds']+investigation['wallSeconds'];logged_total=sum(p['lastSavedElapsedSeconds'] or 0 for p in phases)
data={'topic':topic,'storyMap':spec['storyMap'],'nativeRenderInitial':metrics,'nativeRenderGroundingRework':grounding,'nativeCacheVerification':cache,'renderLogs':phases,'compose':{l:json.loads((job/f'compose_{l}.json').read_text('utf8')) for l in ['ko','en']},'technicalQA':qa,'reuse':['Minsu rig/model definitions','shared materials/world style','Galmuri11 + Galmuri11-Bold','one local BGM','three local SFX types'],'newAssets':['explanatory cage cup','movable white lamp','glass wall and particle/light-path schematic'],'additionalExternalLLMCalls':0,'tokenMeasurement':'Session token usage not available; no claimed numerical reduction','limits':report}
data.update(nativeRenderInvestigationRework=investigation,completedFullAndPartialNativeSeconds=active_native_seconds,allLoggedRenderSeconds=logged_total,logTimingScope='Approximate sum of last saved-frame elapsed times, including sample/still/rework/aborted phases; excludes composition and idle time',cacheIntegrity=json.loads((job/'research/cache_integrity.json').read_text('utf8')),gitignore=json.loads((J/'review/gitignore_cleanup.json').read_text('utf8')))
(job/'DELIVERY.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
body='<html><meta charset="utf-8"><title>MINSU V6 EP10</title><body style="max-width:1000px;margin:40px auto;background:#182031;color:#fff;font-family:sans-serif">'
body+='<h1>MINSU EP10 V6 — 리쿠르고스의 컵</h1><video controls style="width:320px" src="../../../exports/MINSU_EP10_V6_LYCURGUS_KO.mp4"></video>'
body+='<p>32초 / 1080×1920 / 30fps / BGM+SFX / TTS 없음</p><p>전체·부분 본편 3D 렌더 합계 '+str(round(active_native_seconds,1))+'초. 샘플·시안·중단을 포함한 로그상 렌더 합계 약 '+str(round(logged_total,1))+'초. 합성·대기 시간 별도.</p><p><a href="https://www.beilstein-journals.org/bjnano/articles/11/2">사실 검증에 사용한 원문 논문</a> · <a href="../../../exports/MINSU_EP10_V6_LYCURGUS_EN.mp4">영어판</a></p><img style="width:100%" src="review/final/reference_comparison.jpg"><pre style="white-space:pre-wrap">'+html.escape(report)+'</pre></body></html>'
(job/'REPORT.html').write_text(body,encoding='utf8');print('Delivery report and separate editorial limitations saved')
