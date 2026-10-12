from pathlib import Path
import json,sys,subprocess
from PIL import Image,ImageDraw
from imageio_ffmpeg import get_ffmpeg_exe
J=Path(__file__).resolve().parent;R=J.parents[1]
out=J/'review';out.mkdir(exist_ok=True)
video=R/'exports/MINSU_EP09_STRIPES_KO.mp4'
p=subprocess.run([get_ffmpeg_exe(),'-v','error','-i',str(video),'-f','null','-'],capture_output=True)
spec=json.loads((J.parent/'minsu_v5/ep09/episode.json').read_text(encoding='utf8'))
ui=json.loads((J.parent/'minsu_v5/ep09/final/ui_ko.json').read_text(encoding='utf8'))
changes=[];previous=None
for i,row in enumerate(ui if isinstance(ui,list) else ui['frames']):
 texts=[t['text'] for t in row['texts']]
 if texts!=previous:changes.append({'frame':i,'time':round(i/30,3),'texts':texts});previous=texts
(out/'ui_text_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
caption_changes=[];previous=None
for i,row in enumerate(ui if isinstance(ui,list) else ui['frames']):
 texts=[t['text'] for t in row['texts'] if 1450<=t['rect'][1]<1676]
 if texts!=previous:caption_changes.append({'frame':i,'time':round(i/30,3),'texts':texts});previous=texts
(out/'caption_changes.json').write_text(json.dumps(caption_changes,ensure_ascii=False,indent=2),encoding='utf8')
sheet=Image.new('RGB',(900,1600),'#182031')
for i,t in enumerate([0.5,2,5,9,13,17,21,25,29,33,35]):
 file=out/f'ep09_{t:05.1f}.png'
 subprocess.run([get_ffmpeg_exe(),'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-y',str(file)],check=True)
 im=Image.open(file);im.thumbnail((225,400));sheet.paste(im,((i%4)*225,(i//4)*400))
sheet.save(out/'ep09_contact.jpg')
report='''# EP09 시청자 관점 재검토
검사 범위: 전체 MP4 디코드, 실제 출력 프레임, 합성 자막 기록. 실시간 재생·청취·실제 시청자 테스트는 수행하지 못했다.

|시간|문제|수정 이유|
|---|---|---|
|0–4초|고정 제목과 챕터가 먼저 읽히고 말과 등에가 작다|첫 사건을 확대하고 질문은 행동 이후 표시|
|4–8초|옷 교체 행동보다 라벨·패널이 우세|캐릭터 손과 대상의 접촉을 화면 중심에 배치|
|8–12초|같은 비교 구도가 반복되고 연구 정보가 상시 표시|필요한 조건만 남기고 관찰 행동을 이어가기|
|12–16초|확대 장면 진입이 컷 번호에 의존|관찰한 같은 표면으로 확대하고 진입 이유를 행동으로 표현|
|16–20초|체크무늬 발견과 일반 설명의 화면 에너지 차이가 작다|실제 착륙 차이 순간에만 카메라·임팩트·SFX 집중|
|20–28초|대비·가설 설명이 유사한 두 패널 구도로 길게 이어짐|필요한 설명을 압축하고 가설과 관찰 결과를 구분|
|28–36초|반복 비교·작은 문구가 결론의 보상을 분산|같은 월드로 돌아와 첫 행동을 재해석; 한계는 짧게 유지|

처음 이탈하고 싶어지는 지점(제작자 판단): 약 4초. 사건이 확장되기보다 동일한 프레임과 새로운 자막만 제공한다.
삭제: 고정 제목, 챕터 번호, 반복 출처, 장식 상태창, 눈에 보이는 결과를 반복하는 라벨.
자막: 4초 경계마다 전체 교체되는 문장 대신 컷과 독립된 의미 단위 타임라인; 연속 구절은 유지.
사실 전달의 한계: 착륙 감소 관찰과 정확한 시각 기제의 가설을 분리해야 한다. 무조건 착륙 불가능하다고 표현하지 않는다.
수정 목표: 전체 3D 행동 → 관찰한 표면 확대 → 같은 상태로 복귀. 기술적 디코드 성공은 재미의 합격을 의미하지 않는다.
'''
report+='\n본문/강조 자막 실제 교체 시점: '+', '.join(str(c['time'])+'초' for c in caption_changes)+'\n상시 UI·라벨 변동은 ui_text_changes.json으로 분리했다.\n'
(out/'EP09_AUDIT.md').write_text(report,encoding='utf8')
print(json.dumps({'decodeExit':p.returncode,'captionChanges':len(caption_changes),'uiTextChanges':len(changes),'contact':str(out/'ep09_contact.jpg')}))
