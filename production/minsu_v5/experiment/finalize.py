"""Record observed source evidence and measured implementation limits."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,subprocess,time,csv,json,html
from PIL import Image,ImageDraw
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent))
from common import read,write,sha,ROOT

review=E/'review';now=datetime.now(timezone(timedelta(hours=9))).isoformat();source=read(review/'straw/source.json')
observations=[
 {'range':'00:00–00:17','observation':'실물 컵/빨대로 시작해 2개·1개 예상과 설문 수치를 제시한다. 제목, 챕터 1/8, 숫자 HUD, 아래 관객 영역을 유지한다.','timingPurpose':'일상 물체를 본 뒤 의견 차이가 생기도록 한다.','limit':'설문은 영상에 표시된 내용이며 이 작업에서 독립적으로 사실 확인하지 않았다.'},
 {'range':'00:19–00:39','observation':'입구 2, 이어진 길 1, 뚫은 자국 0을 노랑·민트·보라로 구분한다. 사전 정의 패널이 숫자 차이를 설명한다.','timingPurpose':'숫자보다 먼저 무엇을 세는지 분리한다.'},
 {'range':'00:40–00:53.5','observation':'늘이기·누르기·구부리기에 초록 체크, 붙이기·찢기·뚫기에 빨간 실패 표시가 붙는다. 정확 추출 50.50초에는 뚫기 전 구멍 0, 51.00초에는 관통 모습과 HUD 1, 51.50초에는 구멍 0→1 패널과 실패 표시가 함께 보인다.','timingPurpose':'동작→관찰값 변화→규칙 위반 피드백 순서로 이해를 연결한다.','limit':'0.5초 샘플 사이의 정확한 이벤트 프레임과 효과음 시점은 미측정.'},
 {'range':'00:53.5–00:83','observation':'머그컵을 도넛으로, 빨대를 짧게 눌러 고리/도넛으로 바꾼다. 변형 뒤 구멍 1개 결과와 위아래 입구 라벨을 붙인다.','timingPurpose':'새 무대 대신 같은 대상의 연속 변형으로 앞 규칙을 적용한다.'},
 {'range':'00:85–00:107','observation':'단추, 한쪽 끝을 막은 빨대, 발가락 쪽이 열린 양말로 사례를 바꾼다. 입구와 뚫린 길을 계속 대조한다.','timingPurpose':'사례를 바꿔 이전 결론이 우연이 아님을 보여준다.'},
 {'range':'00:109–00:129','observation':'종이 말아 붙이기와 컵/빨대의 내부 고리 비교를 제시한다. 122초에는 같은 위치의 두 대상, 126초에는 한쪽 고리는 작아지고 다른 쪽은 걸리는 결과가 보인다.','timingPurpose':'대안 정의의 한계를 실제 구조 변화와 비교로 설명한다.'},
 {'range':'00:131–00:153','observation':'영상은 조건을 붙인 구멍=입구−1 표현을 컵·빨대·바지·티셔츠에 적용한다.','timingPurpose':'같은 원리를 다른 물체에 적용하는 보상을 만든다.','limit':'해당 표현을 모든 위상 공간에 통하는 일반 공식으로 채택하지 않는다. 별도 소재 제작 시 수학적 조건과 출처 검증 필요.'},
 {'range':'00:155–00:176.21','observation':'빨대 옆을 찌르는 새 실험 후 163초에는 전1/후2 결과가 보인다. 마지막에는 원래의 2·0·1 정의를 정리하고 선택을 묻는다.','timingPurpose':'처음 질문을 이해한 상태에서 참여하게 한다.'}
]
write(review/'straw/observations.json',{'source':source,'observations':observations,'viewingScope':'88 overview samples plus 24 exact-time decoded frames; audio not listened; source science not independently verified','notCopied':['audience sprites','striped straw asset','script','poll data','unknown shader code']})
csvpath=ROOT/'research/reel_observations.csv'
with csvpath.open(encoding='utf-8',newline='') as f:fields=next(csv.reader(f))
row={k:'' for k in fields};row.update(reference_id='R-STRAW-U092',handle='미확인',reel_url='미확인 — 사용자 로컬 MP4',collected_at=now,evidence_file='production/minsu_v5/experiment/review/straw/observations.json',duration_seconds=176.21,opening_timecode='00:00–00:09',opening_text='빨대 구멍은 몇 개?',opening_visual='컵에 꽂힌 빨대에서 빨대 단독 실험으로 전환',visual_style='지속 게임쇼 프레임·챕터·상태 HUD·디더링이 보이는 3D 대상',camera_pov='중앙 실험 대상 고정 무대 및 비교 구도',subtitle_notes='정의별 선택 색상과 별도 하단 설명',narration_notes='미청취',music_notes='미청취',sfx_notes='미청취',story_timecodes='0 사건;19 정의;40 변형;54 전이;85 반례;109 구조 비교;131 다른 물체;155 최종 실험',ending_timecode='02:47–02:56.21',ending_notes='처음 질문과 정의별 답으로 회귀',cta_notes='원래 몇 개라고 생각했는지 선택 요청',observation_limits='원본 로컬 MP4의 표본 프레임 관찰. 실시간 재생/오디오 청취/독립 과학 검증은 수행하지 않음.')
if 'R-STRAW-U092' not in csvpath.read_text('utf-8'):
    with csvpath.open('a',encoding='utf-8',newline='') as f:csv.DictWriter(f,fieldnames=fields).writerow(row)

# Preserve the cold render receipt before checking a genuine warm native-cache run.
cold=read(review/'render_metrics.json');write(review/'cold_render_metrics.json',cold)
with (review/'warm_render.log').open('w',encoding='utf-8') as f:
    cmd=['C:/Program Files/Blender Foundation/Blender 5.0/blender.exe','-b','--python-exit-code','1','--python',str(E/'render.py')]
    result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
if result.returncode:raise RuntimeError('Warm cache verification failed')
warm=read(review/'render_metrics.json');assert warm['renderedFrames']==0 and warm['reusedFrames']==150
write(review/'warm_render_metrics.json',warm);write(review/'render_metrics.json',cold)

images=[('REFERENCE 51.50s',review/'straw/exact_051.50.png'),('REFERENCE 74.00s',review/'straw/exact_074.00.png'),('TECHNICAL FIXTURE 3.53s',review/'decoded_106.png')]
sheet=Image.new('RGB',(540*3,1000),'#18152b');d=ImageDraw.Draw(sheet)
for i,(label,path) in enumerate(images):
    with Image.open(path) as im:sheet.paste(im.resize((540,960),Image.Resampling.NEAREST),(540*i,40))
    d.text((540*i+12,14),label,fill='white')
sheet.save(review/'reference_comparison.jpg',quality=95)
raw=Image.open(review/'post_off.png');decoded=Image.open(review/'decoded_106.png');crops=Image.new('RGB',(960,640),'#18152b');d=ImageDraw.Draw(crops)
regions=[('OBJECT EDGE',(140,500,460,780)),('BODY GLYPHS',(300,1440,620,1720))]
ref=Image.open(review/'straw/exact_074.00.png')
for row,(label,box) in enumerate(regions):
    d.text((8,row*320+4),label+' / OFF | ENCODED | REFERENCE',fill='white')
    crops.paste(raw.crop(box),(0,row*320+28));crops.paste(decoded.crop(box),(320,row*320+28))
    rb=(210,570,530,850) if row==0 else (180,980,500,1260);crops.paste(ref.crop(rb),(640,row*320+28))
crops.save(review/'pixel_comparison.png')
qa=read(review/'technical_qa.json');checks=read(review/'operation_tests.json');palette=read(E/'profile.json')
qa['strawOriginalCompared']=True;qa['referenceEvidence']='straw/observations.json';write(review/'technical_qa.json',qa)
report={'status':'TECHNICAL_STYLE_PREVIEW_COMPLETE','source':source['path'],'sourceDuration':176.21,'sourceOriginalCompared':True,'sourceScienceIndependentlyVerified':False,
 'modules':['experiment/state.py','experiment/operations.py','experiment/overlay.py','experiment/render.py','experiment/profile.json','directors.py','config/RULE_RESOLUTION.json'],
 'implemented':['persistent UI frame and 7 typography roles','5 numeric channels with provenance/unit/definition checks','geometry-completion receipts before state value commit','13 reusable Blender operations; Boolean Cut/Pierce/Join','native ordered dither and fixed background noise; Nearest 2x; separate UI; optional 6% fixed scanlines','compact experiment contract integrated into episode briefing; source selection preserved'],
 'timing':{'barCompletionFrame':75,'barValueUpdateFrame':76,'elbowCompletionFrame':105,'elbowValueUpdateFrame':106},
 'metrics':{'coldNative':cold,'lastCompositionSeconds':qa['composeSeconds'],'warmNative':warm,'reworkCount':1,'compositionOnlyRevisionCount':2,'pipelineExternalLLMCalls':0,'conversationTokenSavings':'not measured','newGeometryPresets':['BLOCK_BAR','BLOCK_ELBOW'],'reused':['V5 cel material library','Galmuri display/body and glyph/text cache','V5 Blender lighting setup'],'heavyWorkers':1},
 'qa':{'stateTests':14,'operationTests':len(checks['results']),'cacheTests':checks['cacheContracts'],'existingV5Tests':10,'fullMP4Decode':True,'checkedFrames':150,'textCollisions':0,'glyphFallbacks':0,'allFrameGeometryViewportChecks':'PASS','preservedSourceAndDeliveryFiles':len(read(review/'preservation_before.json')),'post':palette['post']},
 'editorial':{'reviewed':'selected actual encoded frames, including action/commit boundaries, plus reference MP4 frames','improved':'camera clipping fixed; before/current values separate; yellow pending numbers become mint only after completion','limits':['This 5-second fixture is not a science episode, entertainment approval or audience test.','Reference has hypothesis/rebuttal/transfer/payoff across 176 seconds; fixture only validates the state/UI connection.','Only Rotate was visually reviewed in this fixture; other operations have evaluated-mesh tests, not artistic or physical-conservation approval.','The generic operation library does not infer scientific properties from arbitrary meshes; each science adapter still needs measurements and independent evidence.','No real-time playback or audio listening; technical fixture intentionally has no audio, episode local BGM/SFX stays intact.']},
 'output':str(ROOT/'exports/MINSU_EXPERIMENT_STYLE_PREVIEW.mp4')}
write(review/'DELIVERY.json',report)
esc=html.escape
body=''.join('<li>'+esc(x)+'</li>' for x in report['implemented'])
obs=''.join('<tr><td>'+esc(o['range'])+'</td><td>'+esc(o['observation'])+'</td><td>'+esc(o['timingPurpose'])+'</td></tr>' for o in observations)
limits=''.join('<li>'+esc(x)+'</li>' for x in report['editorial']['limits'])
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>MINSU 실험 게임쇼 프로필 검수</title><style>body{{max-width:1200px;margin:40px auto;padding:0 24px;background:#211d37;color:#f8f4e6;font:17px/1.7 sans-serif}}a{{color:#8ae7bf}}table{{border-collapse:collapse}}td,th{{padding:12px;border:1px solid #685d82;vertical-align:top}}img{{max-width:100%}}video{{max-width:360px}}code{{color:#ffe17a}}</style><h1>실험 게임쇼 프로필 · 기술 검수</h1><p>사용자 제공 176.21초 빨대 MP4의 표본 프레임을 관찰했다. 실제 원본 셰이더 코드나 효과음 타이밍을 알아낸 것으로 표현하지 않는다. 기존 소재 공급·EP08 결과는 보존했다.</p><p><a href="../../../../exports/MINSU_EXPERIMENT_STYLE_PREVIEW.mp4">5초 기술 프리뷰</a> · <a href="DELIVERY.json">실행 결과</a> · <a href="straw/observations.json">원본 관찰 근거</a></p><video controls src="../../../../exports/MINSU_EXPERIMENT_STYLE_PREVIEW.mp4"></video><h2>반영한 구조</h2><ul>{body}</ul><p>수치 갱신: 막대 75프레임 동작 완료 → 76프레임 90도, 꺾인 모형 105 → 106프레임. 실제 관측 데이터가 아닌 렌더 장면의 회전각임을 화면에 명시했다.</p><h2>원본 관찰</h2><table><tr><th>시간</th><th>화면 근거</th><th>타이밍의 역할</th></tr>{obs}</table><h2>대표 화면 비교</h2><p>왼쪽 두 장은 원본, 오른쪽은 자체 기술 시안. 개별 에셋·관객 스프라이트·대본은 복제하지 않았다.</p><img src="reference_comparison.jpg"><h2>후처리 비교</h2><p>필터 미적용 / 인코딩된 적용 결과 / 원본의 부분 확대. 원본과 자체 시안의 출력 해상도는 서로 다르다. 원본 720×1280·30fps, 시안 540×960 3D → Nearest 2배 → 1080×1920·30fps UI.</p><img src="pixel_comparison.png"><h2>시간·캐시</h2><p>수정 후 3D {cold['wallSeconds']:.2f}초 / 합성 {qa['composeSeconds']:.2f}초. 재실행 {warm['wallSeconds']:.2f}초, 150프레임 모두 캐시 재사용, 3D 재렌더 0. 별도 UI 변경은 합성만 실행했다. 외부 LLM API 추가 호출 0; 대화 토큰 절감률은 측정하지 않았다.</p><h2>기술 QA와 한계</h2><p>상태 14 + 메시 연산 13 + 캐시 2 + 기존 V5 10 검증 통과. 150프레임 창 밖 오브젝트·자막 충돌·글리프 폴백 없음. MP4 전체 디코드 통과. 미술·과학·시청 재미를 자동 승인하지 않는다.</p><ul>{limits}</ul></html>'''
# report/review is four directory levels below the project root.
(review/'REPORT.html').write_text(page,'utf-8')
with (ROOT/'PROMPT_LOG.md').open('a',encoding='utf-8') as f:
    f.write('\n\n### U-091/U-092, P-047/P-048 실행 결과\n'+now+'\n빨대 원본 MP4(176.21초,720×1280,30fps)의 표본 프레임과 세부 타임코드 관찰을 기록했다. 실험 상태·동작 완료 후 수치 갱신·색상·공통 UI 프로필 및 실제 Blender 연산을 구현하고 5초 1080×1920 기술 시안을 렌더했다. 최초 가장자리 잘림은 카메라 수정 후 전150프레임 투영 검사 통과. 생성: exports/MINSU_EXPERIMENT_STYLE_PREVIEW.mp4. 원본 비교와 남은 한계: production/minsu_v5/experiment/review/REPORT.html. 새 과학 에피소드나 모든 연산의 미술·물리 검수 완료로 주장하지 않는다.\n')
print(json.dumps({'coldNativeSeconds':cold['wallSeconds'],'warmNativeSeconds':warm['wallSeconds'],'reusedFrames':warm['reusedFrames'],'report':str(review/'REPORT.html')},ensure_ascii=False))
