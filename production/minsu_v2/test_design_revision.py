"""Failure-path regression checks; no rendering, synthesis or topic selection."""
import json,subprocess,sys,unittest,hashlib
from pathlib import Path
from audio import MusicLibrary,validate_audio_events,ASSETS
from layout import place_label,intersects
R=Path(__file__).resolve().parent

class DesignRevisionTests(unittest.TestCase):
    def test_content_does_not_silently_regenerate_ep04(self):
        p=R/'episode.json';before=hashlib.sha256(p.read_bytes()).hexdigest()
        result=subprocess.run([sys.executable,str(R/'content.py')],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(before,hashlib.sha256(p.read_bytes()).hexdigest())

    def test_label_avoids_face_and_action(self):
        protected=[(400,440,800,810),(130,880,720,1120)]
        rect=place_label((480,680),(240,70),protected)
        self.assertFalse(any(intersects(rect,p) for p in protected))

    def test_no_room_is_reported(self):
        with self.assertRaises(ValueError):place_label((400,600),(240,70),[(0,0,1080,1920)])

    def test_music_needs_mood(self):
        with self.assertRaises(ValueError):MusicLibrary().select(None)

    def test_unknown_mood_has_no_fallback(self):
        with self.assertRaises(ValueError):MusicLibrary().select('unavailable_mood')

    def test_event_requires_visible_action(self):
        catalog=json.loads((ASSETS/'catalog.json').read_text('utf-8'))
        with self.assertRaises(ValueError):validate_audio_events(10,[{'time':1,'sound':'water_drop'}],catalog)

    def test_invalid_event_time_or_boost_fails(self):
        catalog=json.loads((ASSETS/'catalog.json').read_text('utf-8'))
        for time,gain in [(float('nan'),-3),(-1,-3),(10,-3),(1,10)]:
            with self.subTest(time=time,gain=gain),self.assertRaises(ValueError):
                validate_audio_events(10,[{'time':time,'gainDb':gain,'sound':'water_drop','event':'contact'}],catalog)

    def test_existing_audio_events_still_valid(self):
        catalog=json.loads((ASSETS/'catalog.json').read_text('utf-8'))
        for name in ('episode.json','audio_ep04_v1.json'):
            spec=json.loads((R/name).read_text('utf-8'))
            self.assertTrue(validate_audio_events(spec['duration'],spec['audioEvents'],catalog))

if __name__=='__main__':unittest.main()
