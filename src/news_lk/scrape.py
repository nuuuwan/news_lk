import os
import re

from bs4 import BeautifulSoup
from utils import cache, ds, filex, hashx, www

from news_lk import _constants, _utils

PRODUCTION_MODE = False


@cache.cache(_constants.CACHE_NAME, _constants.CACHE_TIMEOUT)
def cached_read(url):
    return www.read(url, use_selenium=True)


def _filter_article_links(url):
    if not url:
        return False
    results = re.search(r'.*/\d{3}-\d{6}', url)
    if results:
        return True
    return False


def get_link_urls(url):
    html = cached_read(url)
    soup = BeautifulSoup(html, 'html.parser')
    link_urls = [a.get('href') for a in soup.find_all('a')]
    link_urls = ds.unique(link_urls)
    link_urls = list(filter(_filter_article_links, link_urls))
    _utils.log.info('Scraped %d links from %s', len(link_urls), url)
    if not PRODUCTION_MODE:
        link_urls = link_urls[:3]
    return link_urls


def download(url):
    h = hashx.md5(url)
    dir_h = '/tmp/%s' % (h[0])
    os.system('mkdir -p %s' % dir_h)
    html_file = '%s/%s.html' % (dir_h, h)
    html = cached_read(url)
    filex.write(html_file, html)
    _utils.log.info('Wrote %dKB to %s', len(html) / 1000.0, html_file)


def _scrape():
    link_urls = get_link_urls('https://www.dailymirror.lk/')
    for url in link_urls:
        download(url)


if __name__ == '__main__':
    _scrape()
