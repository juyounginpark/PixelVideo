import unittest,copy,tempfile
from common import *
from typography import TypographyTheme,Overlay
from directors import story_checks,episode_brief
from topic_history import duplicate
from PIL import Image

class Contracts(unittest.TestCase):
 def setUp(self):self.spec=read(R/'ep08/episode.json');self.s=copy.deepcopy(self.spec['shots'][0]);self.key=native_key(self.s,[540,960])
 def test_caption_change_does_not_render_3d(self):
  self.s['captionPlan'][0]['lines']=['Changed'];self.assertEqual(self.key,native_key(self.s,[540,960]))
 def test_camera_change_invalidates_only_changed_shot(self):
  keys=[native_key(s,[540,960]) for s in self.spec['shots']];self.spec['shots'][2]['cameraPlan']['scale']+=.1
  self.assertEqual([i for i,(a,b) in enumerate(zip(keys,[native_key(s,[540,960]) for s in self.spec['shots']])) if a!=b],[2])
 def test_action_change_invalidates(self):
  self.s['scene']['action']='THINK';self.assertNotEqual(self.key,native_key(self.s,[540,960]))
 def test_audio_change_preserves_native(self):
  self.spec['audio']['energy'][0]['db']=-12;self.assertEqual(self.key,native_key(self.spec['shots'][0],[540,960]))
 def test_missing_glyph_fails(self):
  with self.assertRaises(ValueError):TypographyTheme().check(chr(0x10ffff),'PIXEL_BODY')
 def test_unverified_subject_fails(self):
  self.spec['verificationStatus']='ALLEGED'
  with self.assertRaises(ValueError):validation(self.spec)
 def test_noninteger_upscale_fails(self):
  with self.assertRaises(ValueError):Overlay().frame(Image.new('RGB',(500,900)),self.s,0,{})
 def test_story_is_not_automatically_approved(self):
  self.assertFalse(story_checks(self.spec)['automaticEditorialPass'])
 def test_duplicate_current_episode_detected(self):
  self.assertTrue(duplicate({'topicId':self.spec['topicId']},[{'topicId':self.spec['topicId']}]))
 def test_protected_subject_collision_fails(self):
  o=Overlay();o.type.preflight(self.spec)
  with self.assertRaises(ValueError):o.frame(Image.new('RGB',(540,960)),self.s,15,{'head':{'rect':[0,0,1080,1920],'point':[540,960]}})
if __name__=='__main__':unittest.main()
