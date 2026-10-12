from pathlib import Path
import json
from audio import generate_assets, AudioSynchronizer, mux
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
spec=json.loads((R/'episode.json').read_text('utf-8'))
generate_assets()
mix=AudioSynchronizer().build(spec['duration'],spec['audioEvents'],R/'audio_mix_v2',track_id='curious_desert_100',mood='exploration')  # Historical EP04 delivery only.
report=mux(ROOT/'exports/MINSU_EP04_V2_SILENT.mp4',mix,ROOT/'exports/MINSU_EP04_V2_BGM_SFX.mp4')
(R/'audio_mix_v2/aac_measurement.json').write_text(json.dumps(report,indent=2),'utf-8')
print('AUDIO_DELIVERED',report['input_i'],report['input_tp'])
