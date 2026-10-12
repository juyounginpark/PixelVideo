from pathlib import Path
import sys,shutil,json
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent/'minsu_v5'));sys.path.append(str(J.parent/'minsu_v2'))
from audio_direction import build
from audio import mux
target=J.parents[1]/'exports/MINSU_V6_ACTION_EXPLAIN_SAMPLE.mp4';silent=J/'sample/silent.mp4'
if not silent.exists():shutil.copy2(target,silent)
folder=J/'sample/audio';folder.mkdir(exist_ok=True)
events=[{'frame':33,'time':1.1,'sound':'discovery','gainDb':-10,'event':'FAILED_LANDING','duck':True},{'frame':90,'time':3,'sound':'soft_whoosh','gainDb':-12,'event':'MACRO_ENTRY','duck':False},{'frame':246,'time':8.2,'sound':'achievement','gainDb':-10,'event':'WORLD_PAYOFF','duck':True}]
settings={'tts':False,'track':'curious_desert_100','mood':'observation','energy':[{'time':0,'db':-5},{'time':3,'db':-8},{'time':7.9,'db':-12},{'time':8.2,'db':-4},{'time':9.9,'db':-12}]}
mix=build(10,events,folder,settings);mux(silent,mix,target)
qa=json.loads((folder/'audio_qa.json').read_text('utf8'));qa['intentionalPreDiscoveryDip']='7.9s authored gain -12dB';qa['reviewScope']='Event timing/amplitude analysis only; no real-time hearing';(folder/'audio_qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8');print('Sample BGM/SFX added, TTS absent')
