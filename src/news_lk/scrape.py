from bs4 import BeautifulSoup
from utils import cache, ds, www

from news_lk import _constants, _utils


@cache.cache(_constants.CACHE_NAME, _constants.CACHE_TIMEOUT)
def cached_read(url):
    return www.read(url, use_selenium=True)


def _filter_article_links(url):
    if not url:
        return False
    if 'https://www.dailymirror.lk' not in url:
        return False
    tokens = url.split('/')
    return len(tokens) > 6


def get_link_urls(url):
    html = cached_read(url)
    soup = BeautifulSoup(html, 'html.parser')
    link_urls = [a.get('href') for a in soup.find_all('a')]
    link_urls = ds.unique(link_urls)
    link_urls = list(filter(_filter_article_links, link_urls))
    _utils.log.info('Scraped %d links from %s', len(link_urls), url)
    return link_urls


def _scrape():
    link_urls = get_link_urls('https://www.dailymirror.lk/')
    for url in link_urls:
        print(url)


if __name__ == '__main__':
    _scrape()
