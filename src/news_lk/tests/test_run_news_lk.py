"""Tests for news_lk."""

import unittest

from news_lk import run_news_lk


class TestCase(unittest.TestCase):
    """Tests."""

    def test_dump(self):
        """Test."""
        self.assertTrue(run_news_lk._dump())


if __name__ == '__main__':
    unittest.main()
