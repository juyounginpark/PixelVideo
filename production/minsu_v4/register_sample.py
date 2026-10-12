"""Record an actual visual review, then confirm one existing-list topic."""
from common import R,ROOT,read,write,sha,config
sample=ROOT/'exports/MINSU_V4_GRAVITY_SAMPLE.mp4';qa=read(R/'ep07/sample_review/decode_qa.json')
assert qa['sha256']==sha(sample) and qa['decodedFrames']==210 and not qa['preservationChanges']
gate=dict(decision='PROCEED_WITH_STATED_LIMITS',reviewer='Codex visual inspection',evidence=['S05_sequence.jpg','S06_sequence.jpg','S05_104.png','S06_088.png','S06_032.png'],videoSha256=sha(sample),findings=['실제 210프레임 MP4에서 0.267초 간격+정확한 사건 프레임 관찰','S05 범례 이동 뒤 후반 별/화살표와 겹치지 않음','S06 진행 화살표 제거 후 느림/빠름 라벨과 별의 실제 움직임이 구분됨','민트 중력 화살표는 안쪽 방향; 동일 반지름에서 빠른 쪽이 더 큰 필요한 중력','360px 모바일 대표 프레임에서 한글 본문/영어 보조/라벨 읽기 확인','글리프 폴백 없음; 네이티브540→1080정수확대와 별도UI'],limits=['Human listening and real-time playback not performed','Audience comprehension/retention not measured','이후 인물/결말 수정은 이 샘플의 과학 궤적을 변경하지 않지만 보수적 코드 캐시 때문에 최종 재렌더될 수 있음'])
write(R/'ep07/sample_review/GATE.json',gate)
write(R/'config/TEMPLATE_REGISTRY.json',dict(version='4.0.0',sampleGate=str(R/'ep07/sample_review/GATE.json'),sampleHash=sha(sample),registered=['STYLE_SPEC','TYPOGRAPHY_THEME','EFFECT_PRESETS','CAMERA_PRESETS','CHARACTER_MANIFEST','ASSET_MANIFEST','SCENE_SCHEMA','QA_RULES'],scope='reviewed 7s science segment; final character/whole-story review still required'))
s=read(R/'ep07/episode.json');assert s['source']['sha256']==sha(ROOT/s['source']['path'])
receipt=dict(topicId=s['topicId'],name=s['topic'],source=s['source'],criteria='prompts/MYSTERY_100_v1.md',criteriaHash=sha(ROOT/'prompts/MYSTERY_100_v1.md'),selection='confirmed after sample visual gate',excludedPrior=['미스터리 자판기','브로켄','가시도마뱀','브라질너트','얼음','움직이는 돌 기획'],newSupplyItemsAdded=0,originalSupplyModified=False)
write(R/'ep07/source_receipt.json',receipt);s['status']='selected';write(R/'ep07/episode.json',s);print('Sample reviewed; template registered; existing row 8 confirmed')
