"""Cut-independent captions and explicit explanation continuity contracts."""
import re
def reading_time(text):
 return min(3.6,max(1.4,.4+len(re.findall('[가-힣]',text))/8))
def validate_story(shots):
 for i,s in enumerate(shots):
  if not s.get('newInformation') or not s.get('visualAction'):raise ValueError('Empty story beat')
  if s['mode']=='EXPLAIN_SCENE':
   for k in ('entryReason','returnReason','continuityObject','worldSnapshot'):
    if not s.get(k):raise ValueError('Explanation lacks '+k)
   if not any(t['mode']=='WORLD_RETURN' and t.get('worldSnapshot')==s['worldSnapshot'] for t in shots[i+1:]):raise ValueError('No matching world return')
class CaptionDirector:
 def __init__(self,cues):
  self.cues=cues
  for c in cues:
   if len(c['lines'])>2:raise ValueError('Caption exceeds two lines')
   if c['end']-c['start']<reading_time(c.get('newText',''.join(c['lines']))):raise ValueError('Caption too fast')
 def active(self,frame):
  t=frame/30
  for i,c in enumerate(self.cues):
   if c['start']<=t<c['end']:
    previous=self.cues[i-1]['lines'] if i else []
    return c,[1 if line in previous and i and self.cues[i-1]['end']==c['start'] else min(1,(frame-round(c['start']*30)+1)/4) for line in c['lines']]
  return None,[]
