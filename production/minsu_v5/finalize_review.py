from common import *
from datetime import datetime,timezone,timedelta
job=R/'ep08';evidence=[R/'review/final/cut_grid.jpg',R/'review/final/discovery_sequence.jpg',R/'review/final/return_sequence.jpg',R/'review/english/cut_grid.jpg',R/'review/comparison/reference_comparison.jpg',R/'review/comparison/reference_pixel_crops.png',R/'review/audio_envelope.png']
qa=[read(job/'final'/f'qa_{x}.json') for x in ['ko','en']]
assert all(q['technical']=='PASS' for q in qa)
result=dict(decision='DELIVER_WITH_EDITORIAL_LIMITS',reviewer='assistant inspecting actual decoded MP4 frames',audienceTest=False,humanRealtimePlayback=False,humanListening=False,evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in evidence],findings={
 'hook':'첫 프레임부터 우산과 붉은 빗방울이 보인다. 제목만으로 현상을 설명하던 EP07보다 구체적이다.',
 'causality':'입자 침강→현미경 확대→배양 성장→조류 포자라는 조사 결론으로 이어진다. 포자의 대량 공중 유입 원리는 미해결로 남긴다.',
 'shotPurpose':'9컷은 사건·채집·침강·미세 관찰·배양·발견 반응·주변 시료 비교·미확인 범위·회귀 결론을 담당한다.',
 'emphasis':'일반 설명의 효과를 줄이고 배양체 성장에 가장 큰 노란 글자·카메라 변화·발견음을 묶었다. 레퍼런스 4의 강한 감정 연기보다는 절제되어 있다.',
 'typography':'같은 역할의 폰트가 통일됐고 한/영 동시 중복을 없앴다. 시료 라벨은 해당 오브젝트의 투영 좌표를 따른다.',
 'character':'우산을 들고 비를 모으며 몸통·고개·팔·다리·표정이 변한다. 실험실 컷은 반응 중심이고 도구를 직접 조작하는 세밀한 연기는 부족하다.',
 'pixelCRT':'최종 MP4 확대 크롭에서 계단 경계와 고정 스캔라인이 확인된다. 레퍼런스보다 CRT 농도가 약하며 모바일 가독성을 우선한 선택이다.',
 'style':'따뜻한 마당·실험실과 구분되는 어두운 현미경 세계를 사용한다. 머리카락 모서리 결함은 수정됐다. 일부 작은 소품의 텍셀 밀도 차이는 남아 있다.',
 'ending':'처음의 붉은 비가 작은 생물 입자의 색으로 다시 이해된다. 새로운 미스터리를 덧붙이지 않는다.',
 'audio':'파형에서 발견 직전 BGM 감소와 15.6초 SFX를 확인했다. 실제 청취 승인으로 간주하지 않는다.'},limitations=['관객 완주율과 재미를 실측하지 않았다.','손·시선·접촉 동작은 레퍼런스 대비 단순하다.','전체 씬의 월드 기준 텍셀 밀도를 완전히 통일하지 못했다.','현미경·배양 장면은 7초간 원형 구도가 이어진다. 정보와 성장 동작은 바뀌지만 더 풍부한 공간 연출 여지가 있다.','실시간 연속 재생 감상·인간 청취 검수는 수행하지 못했다.','향후 새로운 주제의 어댑터·에셋은 별도 구현과 미술 검수가 필요하다.'])
write(job/'final/editorial.json',result)
g=read(job/'gates.json');g['FINAL_QA']=dict(decision='TECHNICAL_PASS_EDITORIAL_QUALIFIED',technical=dict(ko='PASS',en='PASS'),editorial=result['decision'],reports=['final/qa_ko.json','final/qa_en.json','final/editorial.json'],approvedSceneSpecHash=sha(job/'episode.json'));write(job/'gates.json',g)
write(job/'final/code_manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in list(R.glob('*.py'))+list((R/'config').glob('*.json'))})
log=ROOT/'PROMPT_LOG.md';marker='V5 EP08 실행 결과 — P-042~P-046'
if marker not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n### '+marker+'\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n선정: 기존 나무위키 캐시의 케랄라 붉은 비, 편집 평가 93/100. 결과: exports/MINSU_EP08_V5_RED_RAIN_KO.mp4 및 EN.mp4. 34초, 1080×1920, 30fps, TTS 없음. 정지 프레임→4초 샘플→전체 저해상도 프리뷰→라벨 재합성→최종 렌더 수행. 기술 QA 양 언어 PASS. 편집 판단과 미해결 한계는 production/minsu_v5/ep08/final/editorial.json. 실제 청취/관객 반응은 미검증.\n')
