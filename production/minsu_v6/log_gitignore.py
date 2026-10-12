from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path(__file__).resolve().parents[2]/'PROMPT_LOG.md';stamp=datetime.now(timezone(timedelta(hours=9))).isoformat()
with p.open('a',encoding='utf8') as f:f.write('\n\n## U-098 — Git ignore 추가\n'+stamp+'\n사용자 원문: 깃이그노어도 추가해줘\n기존 규칙을 유지하고 렌더 캐시·중간 프레임·최종 MP4·임시 스템·로그 제외를 확장. 코드·소재 캐시·폰트 라이선스·재사용 음원·QA JSON 및 보고서 보존. 기존 Git 추적 파일 삭제/추적 해제는 수행하지 않는다.\n')
