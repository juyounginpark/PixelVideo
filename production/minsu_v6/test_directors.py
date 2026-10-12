import unittest
from directors import CaptionDirector,reading_time,validate_story
class DirectorsTests(unittest.TestCase):
 def test_retained_phrase(self):
  d=CaptionDirector([{'start':0,'end':2,'lines':['관찰한다']},{'start':2,'end':4,'lines':['관찰한다','다시 확인'],'newText':'다시 확인'}]);self.assertEqual(d.active(60)[1],[1,.25])
 def test_readability_failure(self):
  with self.assertRaises(ValueError):CaptionDirector([{'start':0,'end':1,'lines':['짧아도 읽을 시간이 필요하다']}])
 def test_explanation_requires_return(self):
  with self.assertRaises(ValueError):validate_story([{'mode':'EXPLAIN_SCENE','newInformation':'원인','visualAction':'확대'}])
 def test_wrong_world_cannot_return(self):
  explain={'mode':'EXPLAIN_SCENE','newInformation':'원인','visualAction':'확대','entryReason':'조사','returnReason':'확인','continuityObject':'잔','worldSnapshot':'before'}
  with self.assertRaises(ValueError):validate_story([explain,{'mode':'WORLD_RETURN','newInformation':'결과','visualAction':'복귀','worldSnapshot':'other'}])
 def test_next_phrase_fades_without_resetting_first(self):
  d=CaptionDirector([{'start':0,'end':2,'lines':['관찰한다']},{'start':2,'end':4,'lines':['관찰한다','다시 확인'],'newText':'다시 확인'}]);self.assertEqual(d.active(63)[1],[1,1])
if __name__=='__main__':unittest.main()
