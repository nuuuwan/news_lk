"""Tests for news_lk."""

import unittest

from utils import timex

from news_lk import _utils


class TestCase(unittest.TestCase):
    """Tests."""

    def test_get_ut(self):
        """Test."""
        ut_cur = timex.get_unixtime()
        for (timestamp_str, expected_ut) in [
            ('21 Jul 2019', 1563647400),
            ('1 day ago', ut_cur - timex.SECONDS_IN.DAY),
            ('2 days ago', ut_cur - timex.SECONDS_IN.DAY * 2),
            ('1 minute ago', ut_cur - timex.SECONDS_IN.MINUTE),
            ('2 minutes ago', ut_cur - timex.SECONDS_IN.MINUTE * 2),
        ]:
            self.assertEqual(
                expected_ut,
                _utils.get_ut(timestamp_str, ut_cur),
            )


if __name__ == '__main__':
    unittest.main()
