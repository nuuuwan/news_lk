"""Tests for news_lk."""

import unittest

import pytest

from news_lk import scrape


class TestCase(unittest.TestCase):
    """Tests."""

    @pytest.mark.slow
    def test_get_link_urls(self):
        """Test."""
        TEST_URL = 'https://www.dailymirror.lk/'
        link_urls = scrape.get_link_urls(TEST_URL)
        self.assertGreater(
            len(link_urls),
            100,
        )
        self.assertIn(
            'https',
            link_urls[0],
        )


if __name__ == '__main__':
    unittest.main()
