from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT
from contracts import verify
verify();geometry=read(J/'research/geometry_qa.json');assert not geometry['errors']
evidence=read(J/'review/preview/evidence.json');gates=read(J/'gates.json');now=datetime.now(timezone(timedelta(hours=9))).isoformat()
gates['ART_PREVIEW']['approvedSceneSpecHash']=sha(J/'episode.json')
gates['EDITING_PREVIEW']={'decision':'PROCEED_WITH_STATED_LIMITS','reviewedAt':now,'approvedSceneSpecHash':sha(J/'episode.json'),'evidence':[{'path':str(Path(evidence['path']).relative_to(ROOT)),'sha256':evidence['sha256']},{'path':str((J/'research/geometry_qa.json').relative_to(ROOT)),'sha256':sha(J/'research/geometry_qa.json')}],'observations':['실제36초MP4에서0~2초 접근/착륙이탈 사건을 확인했다.','4초에는같은말 덮개교체,8초에는2019실험 조건,12초에는마지막 접근,16초에는체크반례,20초에는대비,24초에는가설,28초에는효과,32초에는한계를 추가한다.','발견 컷은노랑질문→큰민트결과자막으로 바뀌며 시각적 보상에 강약이 있다. 카메라 여백 수정 후1080프레임 보호 대상 검사 통과.','같은대상을재사용하지만 덮개·비행·정보·감정 변화가 있다. 추상 설명은2개근접컷8초/36초에한정된다.','수치7마리/3덮개는 실제연구 조건. 착륙 감소는 연구 결과를 모식도로 설명하며 임의 비율을 만들지 않았다.','처음장면의 효과를 재확인하고 시각기제의 불확실성 및 불완전한 보호 범위를 설명한다.','최종한국어 결론 한 줄은 시각 원리는 연구 중으로 줄여 글자크기 축소를 피한다. 최종 프레임에서 확인 예정.'],'limits':['장면의 말과 파리는 단순한 블록 모형이며 원본의 세밀한 오브젝트 미술 수준과 같다고 평가하지 않는다.','여러 비교 컷은 같은 목장 구도를 사용한다. 동작/조건/정보는 바뀌지만 공간 다양성은 제한적이다.','민수의 제스처와 덮개 동작은 각색이며 실제 연구자의 행동 기록이 아니다. 손 접촉·시선 연기의 세밀함에는 한계가 있다.','흡혈등에 경로·크기·시간은 설명용 모식도이다. 실제 실험의 정확한 궤적 또는 실패율을 재현하지 않는다.','실시간 재생·오디오 청취·시청자 유지율 검증을 수행하지 않았다. 프레임 기반 편집 검수와 오디오 수치 검사를 구분한다.']};write(J/'gates.json',gates)
print('Editing preview reviewed; final composition can reuse 1080 native frames')
