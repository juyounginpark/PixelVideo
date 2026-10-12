import argparse
from datetime import datetime
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import instaloader
from download_reels import download_links, reel_shortcode


class DirectLinkTests(unittest.TestCase):
    def test_tracking_query_not_part_of_shortcode(self):
        self.assertEqual(reel_shortcode('https://www.instagram.com/reel/DeTSMDtqIs2/?utm_source=test'), 'DeTSMDtqIs2')
        for url in ('https://instagram.com.other.invalid/reel/test/', 'https://www.instagram.com/reel/../', 'http://www.instagram.com/reel/test/'):
            with self.assertRaises(argparse.ArgumentTypeError):
                reel_shortcode(url)

    def test_direct_download_does_not_enumerate_profiles(self):
        post = SimpleNamespace(is_video=True, owner_username='pixelithm', date_utc=datetime(2026, 1, 1),
                               video_play_count=123, video_view_count=100, caption='reference caption')
        with tempfile.TemporaryDirectory() as directory, \
             patch('download_reels.instaloader.Post.from_shortcode', return_value=post), \
             patch('download_reels.instaloader.Profile.from_username') as profile_lookup, \
             patch('download_reels.download_video', return_value='downloaded') as download:
            result = download_links(Mock(), ['https://www.instagram.com/reel/TEST/'], Path(directory))
            self.assertEqual(result, 0)
            profile_lookup.assert_not_called()
            download.assert_called_once()

    def test_access_limit_stops_remaining_urls(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch('download_reels.instaloader.Post.from_shortcode', side_effect=instaloader.AbortDownloadException('429')) as lookup:
            result = download_links(Mock(), ['https://www.instagram.com/reel/ONE/', 'https://www.instagram.com/reel/TWO/'], Path(directory))
            self.assertEqual(result, 1)
            lookup.assert_called_once()


if __name__ == '__main__':
    unittest.main()
