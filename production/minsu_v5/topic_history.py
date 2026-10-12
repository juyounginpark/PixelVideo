"""Extend existing episode metadata for duplicate checks; never replace source stores."""
from common import *

def previous_topics(exclude_job=None):
 rows=[]
 paths=set((ROOT/'production').glob('*/episode.json'))|set((ROOT/'production').glob('*/*/episode.json'))
 for path in sorted(paths):
  if exclude_job and path.parent.resolve()==Path(exclude_job).resolve():continue
  try:s=read(path)
  except (ValueError,OSError):continue
  tid=s.get('topicId') or s.get('sourceTopicId')
  if tid:rows.append(dict(topicId=tid,episode=s.get('episode'),metadata=str(path.relative_to(ROOT))))
 return rows

def duplicate(topic,history):
 return any(t['topicId']==topic['topicId'] for t in history)

if __name__=='__main__':write(R/'research/episode_history.json',previous_topics())
