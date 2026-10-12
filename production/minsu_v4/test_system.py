"""Meaningful invalidation, font-failure and pixel integrity checks."""
import unittest,copy
import numpy as np
from common import R,read,native_key
from typography import TypographyTheme
from adapters import validate_adapter
class CacheContract(unittest.TestCase):
    def setUp(self):self.spec=read(R/'ep07/episode.json');self.shot=self.spec['shots'][0]
    def key(self,s):return native_key(s,[540,960])
    def test_caption_change_does_not_rerender_native(self):
        b=copy.deepcopy(self.shot);b['captionPlan'][0]['english']=['A revised subtitle'];self.assertEqual(self.key(b),self.key(self.shot))
    def test_camera_change_only_affects_that_shot(self):
        changed=copy.deepcopy(self.spec);changed['shots'][2]['cameraPlan']['scale']+=.1
        self.assertEqual([i for i,(a,b) in enumerate(zip(self.spec['shots'],changed['shots'])) if self.key(a)!=self.key(b)],[2])
    def test_action_invalidates(self):
        b=copy.deepcopy(self.shot);b['scene']['speed']+=.1;self.assertNotEqual(self.key(b),self.key(self.shot))
    def test_audio_is_not_native_input(self):
        b=copy.deepcopy(self.spec);b['audio']['track']='edited';self.assertEqual(self.key(b['shots'][0]),self.key(self.shot))
    def test_local_time_relocation_preserves_pixels(self):
        b=copy.deepcopy(self.shot);b['startFrame']+=30;b['endFrame']+=30;self.assertEqual(self.key(b),self.key(self.shot))
    def test_preview_final_are_different(self):self.assertNotEqual(native_key(self.shot,[270,480]),self.key(self.shot))
class PixelTypography(unittest.TestCase):
    def test_missing_glyph_errors(self):
        with self.assertRaises(ValueError):TypographyTheme().check('\U0010ffff','PIXEL_BODY')
    def test_integer_pixel_alpha(self):
        t=TypographyTheme();im=t.line('중력 Gravity','PIXEL_BODY',3,'white','mint',('중력',));a=np.array(im)
        self.assertTrue(set(np.unique(a[:,:,3]))<={0,255})
        self.assertTrue(np.array_equal(a,a[::3,::3].repeat(3,0).repeat(3,1)))
    def test_all_visible_characters(self):self.assertEqual(TypographyTheme().preflight(read(R/'ep07/episode.json'))['fallbacks'],0)
class SourceBoundary(unittest.TestCase):
    def test_unknown_topic_is_not_defaulted(self):
        s=read(R/'ep07/episode.json');s['topicId']='unverified-new-topic'
        with self.assertRaises(ValueError):validate_adapter(s)
    def test_unknown_scene_does_not_fall_back_to_galaxy(self):
        s=read(R/'ep07/episode.json');s['shots'][0]['phase']='unknown'
        with self.assertRaises(ValueError):validate_adapter(s)
if __name__=='__main__':unittest.main()
