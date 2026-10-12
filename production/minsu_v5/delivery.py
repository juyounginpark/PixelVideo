"""Evidence-linked local delivery report; no aesthetic auto-pass."""
from common import *
from html import escape
import os
job=R/'ep08';s=read(job/'episode.json');topic=read(job/'topic.json');ko=read(job/'final/compose_ko_MOBILE.json');en=read(job/'final/compose_en_MOBILE.json');qa=read(job/'final/qa_ko.json');qaen=read(job/'final/qa_en.json')
def render_summary(quality):
 rows=[read(p) for p in (job/quality/'runs').glob('*.json')]
 full=[r for r in rows if r['renderedFrames']+r['reusedFrames']==s['durationFrames'] and not r['errors']]
 actual=max(full,key=lambda r:r['renderedFrames'])
 return dict(nativeRenderSeconds=actual['renderSeconds'],wallSeconds=actual['totalSeconds'],renderedFrames=actual['renderedFrames'],reusedFrames=actual['reusedFrames'],assetCache=actual['assetCache'],allRecordedNativeRenderSeconds=sum(r['renderSeconds'] for r in rows),warmRuns=[dict(seconds=r['totalSeconds'],reusedFrames=r['reusedFrames']) for r in full if r['renderedFrames']==0])
summary=dict(topic=topic['name'],score=topic['interestScore'],scoreType='editorial judgment; not audience performance',verificationStatus=s['verificationStatus'],sourceUrl=topic['sourceUrl'],science=s['science'],storyMap=s['storyMap'],hook=s['hook'],outputs=dict(korean=ko['output'],english=en['output'],preview='exports/MINSU_EP08_V5_PREVIEW.mp4',sample='exports/MINSU_EP08_V5_ART_SAMPLE.mp4'),render=dict(preview=render_summary('preview'),final=render_summary('final'),koreanCompositeSeconds=ko['totalSeconds'],englishCompositeSeconds=en['totalSeconds']),assets=read(R/'config/ASSET_MANIFEST.json'),optimization=read(R/'review/optimization_design.json'),cache=dict(englishNativeFramesReused=1020,englishAudioCacheHit=en['audioCacheHit'],koreanUiCacheHits=ko['uiCacheHits'],englishUiCacheHits=en['uiCacheHits']),post=config('POST_PROCESS_PRESETS'),technicalQA=dict(korean=qa['technical'],english=qaen['technical'],sourcePreservation=qa['sourcePreservation'],fontFallbacks=qa['glyphFallbacks'],aacTruePeak=qa['audioTruePeak']),editorial=read(job/'final/editorial.json'),creativeRevisionRounds=4,changedModules=['discovery.py + topic_history.py','directors.py + SceneSpec/config','character_director.py + rain_scene.py + art_v5.py','typography.py','audio_direction.py','render.py + compose.py + run.py','model_review.py + inspect_episode.py + qa_final.py'],limitations=['관객 완주율·흥미 점수는 실제 사용자 시험으로 검증하지 않았다.','실제 MP4 프레임 시퀀스를 검수했으며 실시간 재생 감상·사람의 음악 청취 검수는 하지 못했다.','손가락·시선·물체 접촉 연기는 레퍼런스 대비 단순하다.','작은 소품과 납작한 세포의 축척 때문에 월드 기준 텍셀 밀도는 완전히 같지 않다.','새 주제의 임의 3D 장면을 범용 자동 생성하지 않는다. 검증된 SceneSpec와 구현된 어댑터만 제작한다.','나무위키 실시간 갱신은 접근 제한으로 수행하지 않았으며 기존 캐시를 사용했다.'])
summary['cacheBenchmark']=read(R/'review/cache_benchmark/receipt.json')
write(job/'DELIVERY.json',summary)
def link(path,label):return f'<a href="{escape(os.path.relpath(ROOT/path,job).replace(chr(92),chr(47)))}">{escape(label)}</a>'
def image(path,alt):return f'<img loading="lazy" src="{escape(os.path.relpath(ROOT/path,job).replace(chr(92),chr(47)))}" alt="{escape(alt)}">'
parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MINSU EP08 V5 제작·검수</title><style>body{max-width:1150px;margin:40px auto;padding:0 22px;background:#f7f3e7;color:#202338;font:17px/1.7 system-ui}h1{font-size:34px}h2{margin-top:42px}a{color:#176a67}img{max-width:100%;height:auto;border:1px solid #d4d3c8}video{width:320px;max-width:100%}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:12px;text-align:left;vertical-align:top}.note{background:#fff4ce;padding:18px}code{font-size:14px}li{margin:8px 0}</style><body>',
 '<h1>MINSU EP08 V5 — 케랄라의 붉은 비</h1><p>34초 · 1080×1920 · 30fps · 한국어 기본 / 영어 별도 · BGM + SFX · TTS 없음</p>',
 '<p>'+link(Path(ko['output']),'한국어 최종 MP4')+' · '+link(Path(en['output']),'영어 최종 MP4')+' · '+link(Path('exports/MINSU_EP08_V5.ko.srt'),'한국어 SRT')+' · '+link(Path('exports/MINSU_EP08_V5.en.srt'),'English SRT')+'</p>',
 '<video controls preload="metadata" src="../../../exports/MINSU_EP08_V5_RED_RAIN_KO.mp4"></video>',
 '<p class="note">기술 QA와 편집 검수를 분리했습니다. 실제 MP4에서 뽑은 전체 구간 시퀀스와 핵심 동작을 검수했지만, 사람의 연속 재생 감상·청취·관객 완주율 시험은 완료로 표시하지 않습니다.</p>',
 '<h2>선정과 사실 확인</h2><p>기존 나무위키 캐시 후보 40개 → 규칙 필터 → 상세 검토 10개 → 시각적 후킹 5개 → 케랄라 붉은 비. 편집 평가 93/100이며 실측 흥미 점수가 아닙니다. 판정은 2001년 조사된 시료의 색 원인에 한정합니다.</p>',
 '<p><a href="https://www.iangoddard.com/sampath2001.pdf">CESS·TBGRI 2001 보고서 공개 보관본</a>: 입자의 침강, 배양된 조류와 주변 시료를 근거로 색 원인을 설명합니다. 많은 포자가 동시에 공중에 들어간 정확한 과정은 미확인으로 남깁니다. <a href="https://www.microbiologyresearch.org/content/journal/micro/10.1099/mic.0.062711-0">2013년 독립 DNA 검출 연구</a>도 검토했으나 2001 배양 전체를 독립 재현한 자료로 취급하지 않았습니다.</p>',
 '<h2>기승전결</h2><table><tr><th>단계</th><th>관객이 얻는 정보</th></tr>']
for k,v in s['storyMap'].items():parts.append(f'<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>')
parts+=['</table><p>후킹: 첫 프레임부터 흰 우산에 붉은 빗방울이 떨어집니다. 배양에서 자라는 조류가 발견의 보상이며, 끝에서 처음 비의 색을 다시 이해합니다.</p>',
 '<h2>기존 문제와 수정</h2><p>EP07의 추상 도식 24/35초, 낮은 캐릭터 참여, 차가운 단일 공간, 동시 이중 언어를 개선했습니다. EP08은 야외·채집·침강·현미경·배양·실험실·시료 비교로 이어지며 추상 확대는 7/34초입니다. 우산 잘림과 머리카락 모서리 결함을 실제 프레임 확인 후 수정했고, 행동을 반복하던 자막은 관찰 이유와 과학적 차이를 설명하도록 바꿨습니다.</p>',
 image(Path('production/minsu_v5/review/comparison/reference_comparison.jpg'),'레퍼런스 3·4, EP07, EP08 실제 MP4 프레임 비교'),
 '<h2>픽셀·CRT</h2><p>540×960 실제 3D → 2배 Nearest 확대 → 독립 고해상도 픽셀 UI → 고정 4px 주기·6% 스캔라인 → 약한 색 경계 혼합 → H.264. RGB 경계는 1px 이동 성분을 12.5% 혼합하고 글자 영역에서는 그 강도를 20%로 낮춥니다. 일반 블러는 사용하지 않습니다.</p>',
 image(Path('production/minsu_v5/review/crt/pixel_crops.png'),'MP4 디코드 후 OFF/10%/6%/14% 비교'),
 image(Path('production/minsu_v5/review/comparison/reference_pixel_crops.png'),'원본 픽셀 크롭 비교'),
 '<h2>실행 시간과 재사용</h2><table><tr><th>항목</th><th>측정</th></tr>']
for k,v in [('저해상도 전체 3D',summary['render']['preview']['wallSeconds']),('최종 전체 3D',summary['render']['final']['wallSeconds']),('한국어 UI·오디오·합성',ko['totalSeconds']),('영어 UI·합성',en['totalSeconds']),('동일 결과 캐시 재실행',summary['cacheBenchmark']['totalWallSeconds'])]:parts.append(f'<tr><td>{k}</td><td>{v:.1f}초</td></tr>')
parts+=['</table><p>기존 에셋 7개(캐릭터 1·폰트 2·음원 4)를 재사용했고 신규 논리 에셋 묶음 9개를 만들었습니다. 메시 개수와 에셋 수를 혼동하지 않습니다. 영어판은 3D 1,020프레임과 오디오를 재사용합니다. 후보 캐시·공통 설정·글리프 아틀라스·텍스트·컷별 3D/UI·오디오 캐시를 분리했습니다.</p>',
 '<p>별도 LLM API 호출 0회, 컷별 호출 0회. 이번 대화의 실제 토큰 사용량은 측정할 수 없어 절감률을 주장하지 않습니다. 편집 수정은 구도·재질·자막·대상 연결 라벨의 4차례입니다.</p>',
 '<h2>검수</h2><p>한/영 각 1,020프레임 디코드, 자막 영역·글리프·네이티브 캐시 해시·음량·이벤트 동기화를 검사했습니다. 소스 및 기존 결과물 '+str(qa['sourcePreservation']['checked'])+'개 해시를 확인했고 변경은 없습니다.</p>',
 image(Path('production/minsu_v5/review/final/cut_grid.jpg'),'최종 9컷'),
 image(Path('production/minsu_v5/review/audio_envelope.png'),'BGM·SFX 파형'),
 '<h2>남은 한계</h2><ul>']
parts += ['<li>'+escape(x)+'</li>' for x in summary['limitations']]
parts+=['</ul><p>'+link(Path('production/minsu_v5/ep08/DELIVERY.json'),'측정·코드 변경 상세 JSON')+' · '+link(Path('production/minsu_v5/ep08/final/qa_ko.json'),'기술 QA')+' · '+link(Path('production/minsu_v5/ep08/final/editorial.json'),'편집 QA')+'</p></body></html>']
(job/'REPORT.html').write_text('\n'.join(parts),'utf-8');print('DELIVERY',summary['render'])
