from pathlib import Path
r=Path(__file__).resolve().parent
t=(r.parent/'minsu_v4/compose.py').read_text('utf-8')
t=t.replace("from audio import AudioSynchronizer,mux,FF,ASSETS","from audio import mux,FF,ASSETS\nfrom audio_direction import build")
t=t.replace("R/'ep07'","R/'ep08'").replace("a=p.parse_args()","p.add_argument('--locale',choices=['ko','en'],default='ko');p.add_argument('--post',choices=['OFF','REFERENCE','MOBILE','STRONG'],default='MOBILE');a=p.parse_args()")
t=t.replace('overlay=Overlay()','overlay=Overlay(a.locale,a.post)').replace("config('EFFECT_PRESETS')","config('EFFECT_LIBRARY')").replace("config('TYPOGRAPHY_THEME')","config('FONT_THEME')")
t=t.replace("key=digest(dict(native=item['key']","key=digest(dict(locale=a.locale,post=a.post,postSettings=config('POST_PROCESS_PRESETS'),native=item['key']")
old="ef=cursor+e['frame'];events.append(dict(frame=ef,time=ef/30,sound=preset['sound'],gainDb=preset['gainDb'],event=s['visualAction'],duck=e['type']=='DISCOVERY'));cursor+=n"
new="ef=cursor+e['frame']\n        if preset['sound']:events.append(dict(frame=ef,time=ef/30,sound=preset['sound'],gainDb=preset['gainDb'],event=s['visualAction'],duck=e['type']=='DISCOVERY'))\n        cursor+=n"
assert old in t;t=t.replace(old,new)
t=t.replace("settings=spec['audio'],events=events","settings=spec['audio'],offset=shots[0]['startFrame']/30,directionCode=sha(R/'audio_direction.py'),events=events")
t=t.replace("AudioSynchronizer().build(cursor/30,events,audio,track_id=spec['audio']['track'],mood=spec['audio']['mood'])","build(cursor/30,events,audio,spec['audio'],shots[0]['startFrame']/30)")
t=t.replace("write(out/('sample_compose.json' if a.shots else 'compose.json'),report)","report.update(locale=a.locale,postPreset=a.post,textCacheHits=overlay.type.cacheHits,textCacheMisses=overlay.type.cacheMisses);write(out/(('sample_'+a.shots if a.shots else 'compose')+'_'+a.locale+'_'+a.post+'.json'),report)")
t=t.replace("write(out/'ui_qa.json',ui_reports)","write(out/('ui_qa_'+a.locale+'_'+a.post+'.json'),ui_reports)").replace('V4_','V5_')
(r/'compose.py').write_text(t,'utf-8')
