"""Failure-path tests for data gates and original audio, not subjective art tests."""
import copy, json, unittest, tempfile
from pathlib import Path
import numpy as np
from PIL import ImageFont
from content import StoryboardDirector, SceneCompiler, TopicScorer
from audio import MusicLibrary, read_wav, ASSETS

class SystemTests(unittest.TestCase):
    def setUp(self):self.spec=StoryboardDirector().ep04()
    def test_missing_source_fails(self):
        self.spec['factCheck'][0]['evidence']=[]
        with self.assertRaises(ValueError):SceneCompiler().validate(self.spec)
    def test_gap_fails(self):
        self.spec['shots'][2]['startTime']+=.1
        with self.assertRaises(ValueError):SceneCompiler().validate(self.spec)
    def test_unknown_character_fails(self):
        self.spec['shots'][0]['characterIds']=['other']
        with self.assertRaises(ValueError):SceneCompiler().validate(self.spec)
    def test_caption_outside_shot_fails(self):
        self.spec['shots'][0]['captionTimeline'][0]['end']=3
        with self.assertRaises(ValueError):SceneCompiler().validate(self.spec)
    def test_audio_outside_shot_fails(self):
        self.spec['shots'][0]['audioEvents'][0]['time']=2
        with self.assertRaises(ValueError):SceneCompiler().validate(self.spec)
    def test_score_threshold(self):
        self.assertFalse(TopicScorer().score(dict.fromkeys(TopicScorer.WEIGHTS,.7))['thresholdPassed'])
    def test_audio_refuses_unlicensed_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            lib=MusicLibrary();lib.path=Path(folder)/'catalog.json'
            lib.path.write_text(json.dumps({'bgm':[{'id':'x','mood':['exploration']}]}))
            with self.assertRaises(ValueError):lib.select('exploration')
    def test_loop_boundary(self):
        x=read_wav(ASSETS/'bgm/curious_desert_100.wav')
        self.assertEqual(len(x),921600)
        self.assertLess(np.max(np.abs(x[0]-x[-1])),.002)
    def test_korean_glyphs(self):
        root=Path(__file__).parent;f=ImageFont.truetype(str(root/'fonts/NanumGothic-ExtraBold.ttf'),66)
        missing=bytes(f.getmask('\u0378'))
        text=''.join(''.join(c['lines']) for s in self.spec['shots'] for c in s['captionTimeline'])
        for char in set(text):
            if '\uac00'<=char<='\ud7a3':self.assertNotEqual(bytes(f.getmask(char)),missing,char)

if __name__=='__main__':unittest.main()
