from common import *
s=read(R/'ep08/episode.json')
def stamp(frame):
 ms=round(frame/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for locale,key in [('ko','lines'),('en','english')]:
 rows=[]
 for shot in s['shots']:
  for caption in shot['captionPlan']:
   rows.append(f"{len(rows)+1}\n{stamp(shot['startFrame']+caption['start'])} --> {stamp(shot['startFrame']+caption['end'])}\n"+'\n'.join(caption[key])+'\n')
 (ROOT/'exports'/f'MINSU_EP08_V5.{locale}.srt').write_text('\n'.join(rows),'utf-8')
