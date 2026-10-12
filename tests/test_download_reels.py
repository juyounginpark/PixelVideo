import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from download_reels import download_video, select_top, valid_handle


def row(code, views, plays=None):
    return {"shortcode": code, "published_at": "2026-10-01T00:00:00+00:00",
            "video_view_count": views, "video_play_count": plays}


class RankingTests(unittest.TestCase):
    def test_highest_views_not_listing_order(self):
        rows = [row("new", 10), row("old", 900), row("middle", 100), row("winner", 1000)]
        selected, metric, status = select_top(rows, 3, True, "auto")
        self.assertEqual([v["shortcode"] for v in selected], ["winner", "old", "middle"])
        self.assertEqual(metric, "video_view_count")
        self.assertEqual(status, "ranked")

    def test_play_count_preferred_only_when_all_present(self):
        selected, metric, _ = select_top([row("a", 900, 100), row("b", 10, 800)], 3, True, "auto")
        self.assertEqual(metric, "video_play_count")
        self.assertEqual(selected[0]["shortcode"], "b")
        _, metric, _ = select_top([row("a", 900, 100), row("b", 10)], 3, True, "auto")
        self.assertEqual(metric, "video_view_count")

    def test_unknown_counts_and_partial_scan_never_rank(self):
        self.assertEqual(select_top([row("a", None)], 3, True, "auto")[2], "missing_counts")
        self.assertEqual(select_top([row("a", 500)], 3, False, "auto")[0], [])
        self.assertEqual(select_top([row("a", None, 10)], 3, True, "video_view_count")[2], "missing_counts")

    def test_zero_is_known_and_fewer_than_three_is_allowed(self):
        selected, _, _ = select_top([row("a", 0)], 3, True, "auto")
        self.assertEqual(len(selected), 1)

    def test_path_traversal_handle_rejected(self):
        import argparse
        for value in ("..", "../escape", "C:\\escape"):
            with self.assertRaises(argparse.ArgumentTypeError):
                valid_handle(value)


class DownloadTests(unittest.TestCase):
    def test_partial_response_not_promoted_to_video(self):
        loader = Mock()
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.headers = {"Content-Length": "100"}
        response.iter_content.return_value = [b"\x00\x00\x00\x18ftypmp42" + b"data"]
        loader.context.get_raw.return_value = response
        post = Mock(video_url="https://example.invalid/test.mp4")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "video.mp4"
            with self.assertRaises(RuntimeError):
                download_video(loader, post, path)
            self.assertFalse(path.exists())
            self.assertTrue(path.with_suffix(".mp4.part").exists())

    def test_existing_video_skips_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "video.mp4"
            path.write_bytes(b"\x00\x00\x00\x18ftypmp42data")
            loader = Mock()
            self.assertEqual(download_video(loader, Mock(), path), "already_present")
            loader.context.get_raw.assert_not_called()


if __name__ == "__main__":
    unittest.main()
