from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path(__file__).resolve().parents[2]/'PROMPT_LOG.md';stamp=datetime.now(timezone(timedelta(hours=9))).isoformat()
with p.open('a',encoding='utf8') as f:f.write('\n\n## U-097 — V6 제작 계속\n'+stamp+'\n사용자 원문: continue\n이전 V6 요청과 EP10 제작을 이어간다. 기존 공급원·에셋·TTS 비활성 규칙 유지.\n')
