"""Append only directly observed local reference evidence to the existing register."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];path=R/'research/reel_observations.csv'
with path.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;existing={r['reference_id'] for r in reader}
rows=[dict(reference_id='USER-REF3-V31',handle='미확인',reel_url='미확인: 사용자 제공 로컬 MP4',collected_at='2026-10-12 (Asia/Seoul), 시각 미기록',
      evidence_file='production/minsu_v31/review/media_evidence.json; review/ref3/sequence_*.jpg',duration_seconds='51.24',opening_timecode='00:01',
      opening_text='똥, 오줌… 왜 말만 들어도 웃길까?',opening_visual='보라색 격자 무대, 인물과 갈색 물체, 큰 녹색 강조 단어',
      visual_style='복셀 형태 3D와 별도 자막·정보 패널',camera_pov='정면 무대 중심; 샘플에서 크기와 좌우 구도 변화 확인',
      subtitle_notes='상단 노란 제목, 중앙 개념 패널, 하단 흰색·녹색 자막. 33–34초 백분율의 과학 근거는 미검증',
      story_timecodes='00:05 금지 표지;00:16 장벽과 녹색 구역;00:22 파티클;00:27 상태 상자;00:35 상태 변화;00:43 개념 결론',
      ending_timecode='00:50',ending_notes='공유 요청 자막',narration_notes='미청취',music_notes='미청취',sfx_notes='미청취',
      observation_limits='전 MP4 1227프레임 디코드, 정확한 1초 간격 화면 검토. 실시간 청취·제작 툴·계정 귀속은 미확인. 시각 변화 시각은 샘플 기준'),
      dict(reference_id='USER-REF4-V31',handle='미확인',reel_url='미확인: 사용자 제공 로컬 MP4',collected_at='2026-10-12 (Asia/Seoul), 시각 미기록',
      evidence_file='production/minsu_v31/review/media_evidence.json; review/ref4/sequence_*.jpg',duration_seconds='30.11',opening_timecode='00:00',
      opening_text='안 만졌는데 왜 간지러울까?',opening_visual='큰 질문과 두 인물, 접근하는 손, 얼굴·팔·몸 자세 반응',visual_style='복셀 형태 인물과 개념 오브젝트, 외곽선 자막, 십자 강조',
      subtitle_notes='도입 대형 흰색·노란 질문, 설명 흰색/녹색, 짧은 소형 상태 문구. 여섯 계층 시스템을 관찰했다고 주장하지 않음',
      story_timecodes='00:00–02 인물;00:03–05 확대 개념;00:06–11 실험실;00:13–14 레이더;00:15–17 인물;00:18–19 방어 비유;00:20–24 원숭이;00:25–29 인물',
      ending_timecode='00:29',ending_notes='인물 반응과 공유 문구',narration_notes='미청취',music_notes='미청취',sfx_notes='미청취',
      observation_limits='전 MP4 720프레임 디코드, 정확한 1초 간격 화면 검토. 컷 경계의 정밀 시각과 원본 SFX는 단정하지 않음')]
with path.open('a',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields)
    for row in rows:
        if row['reference_id'] not in existing:writer.writerow(row)
print('OBSERVATIONS_RECORDED')
