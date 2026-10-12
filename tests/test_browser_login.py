import time
import unittest

from browser_login import instagram_cookies


class CookieScopeTests(unittest.TestCase):
    def test_only_unexpired_instagram_cookies_are_imported(self):
        cookies = [
            {"domain": ".instagram.com", "name": "sessionid", "value": "test-only", "expires": -1},
            {"domain": "instagram.com", "name": "csrftoken", "value": "test-only", "expires": time.time() + 60},
            {"domain": "other.invalid", "name": "other", "value": "excluded", "expires": -1},
            {"domain": "instagram.com.other.invalid", "name": "fake", "value": "excluded", "expires": -1},
            {"domain": ".instagram.com", "name": "expired", "value": "excluded", "expires": 0},
        ]
        self.assertEqual(set(instagram_cookies(cookies)), {"sessionid", "csrftoken"})


if __name__ == "__main__":
    unittest.main()
