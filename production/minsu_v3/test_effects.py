import copy,unittest
from effects import EffectDirector,punch_scale,pop_scale,held_frame,audio_events

def fixture():
    return {'fps':30,'durationFrames':180,'shots':[{'id':'s','startFrame':0,'endFrame':180,
             'actions':[{'id':'a','target':'actor','startFrame':0,'endFrame':180,'visibleChange':'actor steps back'}],
             'captions':[],'events':[{'id':'e','frame':30,'type':'SURPRISE','target':'actor','actionId':'a','intensity':2}]}]}

class EffectsTests(unittest.TestCase):
    def test_no_action_no_effect(self):
        s=fixture();s['shots'][0]['actions']=[]
        with self.assertRaises(ValueError):EffectDirector().compile(s)
    def test_exact_sound_frame(self):
        t=EffectDirector().compile(fixture());self.assertEqual(audio_events(t)[0]['time'],1)
    def test_duplicate_event_rejected(self):
        s=fixture();s['shots'][0]['events']*=2
        with self.assertRaises(ValueError):EffectDirector().compile(s)
    def test_budget_not_quota(self):
        s=fixture();s['shots'][0]['events']=[]
        self.assertEqual(EffectDirector().compile(s)['EffectTimeline'],[])
    def test_clamps_global_zoom_budget(self):
        s=fixture();s['shots'][0]['events']=[dict(s['shots'][0]['events'][0],id=str(i),frame=i*25) for i in range(7)]
        self.assertLessEqual(EffectDirector().compile(s)['counts']['PUNCH_ZOOM'],5)
    def test_data_requires_provenance(self):
        s=fixture();e=s['shots'][0]['events'][0];e.update(type='COMPARISON',data={'label':'value','value':'100'})
        with self.assertRaises(ValueError):EffectDirector().compile(s)
    def test_no_data_no_fake_gauge(self):
        s=fixture();s['shots'][0]['events'][0]['type']='COMPARISON'
        self.assertFalse(EffectDirector().compile(s)['EffectTimeline'])
    def test_caption_not_repeated(self):
        s=fixture();s['shots'][0]['captions']=[{'startFrame':0,'endFrame':180,'lines':['same']}]
        s['shots'][0]['events'][0].update(type='QUESTION',text='same')
        with self.assertRaises(ValueError):EffectDirector().compile(s)
    def test_curve_limits(self):
        self.assertAlmostEqual(punch_scale(.10),1.1);self.assertAlmostEqual(punch_scale(.27),1.04)
        self.assertAlmostEqual(punch_scale(.60),1);self.assertAlmostEqual(pop_scale(0),.75);self.assertAlmostEqual(pop_scale(.10),1.12)
    def test_freeze_holds_same_frame(self):
        s=fixture();s['shots'][0]['events'][0].update(type='IMPACT',freezeAllowed=True)
        t=EffectDirector().compile(s);self.assertEqual(held_frame(32,t),30);self.assertEqual(held_frame(40,t),40)

if __name__=='__main__':unittest.main()
