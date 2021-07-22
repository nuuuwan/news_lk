import os
import re

from bs4 import BeautifulSoup
from utils import cache, ds, filex, hashx, jsonx, timex, www

from news_lk import _constants, _utils

MAX_URLS_TO_DOWNLOAD = 10


def clean(s):
    s = s.replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s)

    for (before, after) in [
        ('\u201c', '"'),
        ('\u201d', '"'),
    ]:
        s = s.replace(before, after)

    return s.strip()


@cache.cache(_constants.CACHE_NAME, _constants.CACHE_TIMEOUT)
def cached_read(url):
    try:
        return www.read(url, use_selenium=True)
    except:
        return None


def _filter_article_links(url):
    if not url:
        return False
    if 'https://www.dailymirror.lk/audio' in url:
        return False
        if 'https://www.dailymirror.lk/awantha' in url:
            return False
    results = re.search(r'.*/\d{3}-\d{6}', url)
    if results:
        return True
    return False


def get_link_urls(url):
    html = cached_read(url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    link_urls = [a.get('href') for a in soup.find_all('a')]
    link_urls = ds.unique(link_urls)
    link_urls = list(filter(_filter_article_links, link_urls))
    link_urls = sorted(link_urls)

    _utils.log.info('Scraped %d links from %s', len(link_urls), url)
    return link_urls


def download(url):
    h = hashx.md5(url)[:8]
    html_file = '/tmp/news_lk.article.%s.html' % (h)

    is_download = False
    if not os.path.exists(html_file):
        html = cached_read(url)
        filex.write(html_file, html)
        _utils.log.info('Wrote %dKB to %s', len(html) / 1000.0, html_file)
        is_download = True

    return url, html_file, is_download


def parse(url, html_file):
    data_file = html_file.replace('.html', '.json')
    if os.path.exists(data_file):
        _utils.log.warn('%s already exists', data_file)
        return

    html = filex.read(html_file)
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h1').text.strip()
    time_str = soup.find('span', class_='gtime').text
    ut = timex.parse_time(time_str, '%d %B %Y %I:%M %p')
    time_id = timex.format_time(ut, '%Y-%m-%d-%H%M')
    paragraphs = []

    # type 1
    header_inner_content = soup.find('header', class_='inner-content')
    for p in header_inner_content.find_all('p'):
        paragraph = clean(p.text)
        if len(paragraph) < 30:
            continue
        paragraphs.append(paragraph)

    # type 2
    if not paragraphs:
        for div in soup.find_all('div'):
            style = div.get('style', '')
            if 'small' not in style:
                continue
            paragraph = clean(div.text)
            if len(paragraph) < 30:
                continue
            paragraphs.append(paragraph)

    data = dict(
        source='www.dailymirror.lk',
        url=url,
        ut=ut,
        time_id=time_id,
        title=title,
        paragraphs=paragraphs,
    )

    jsonx.write(data_file, data)
    _utils.log.info(
        'Parsed %s to %s (%s - "%s", %d paragraphs)',
        html_file,
        data_file,
        time_id,
        title,
        len(paragraphs),
    )


def _scrape():
    MAX_URLS_TO_DOWNLOAD = 3
    link_urls = get_link_urls('https://www.dailymirror.lk/')
    n_downloads = 0
    for url in link_urls:
        url, html_file, is_download = download(url)
        if is_download:
            n_downloads += 1
        parse(url, html_file)

        if n_downloads >= MAX_URLS_TO_DOWNLOAD:
            break


if __name__ == '__main__':
    _scrape()
