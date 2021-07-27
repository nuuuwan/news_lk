import os
import re

from bs4 import BeautifulSoup
from utils import cache, ds, filex, hashx, jsonx, timex, tsv, www

from news_lk import _constants, _utils

MAX_URLS_TO_DOWNLOAD = 5


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
    return www.read(url, use_selenium=True)


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
    html_file = '/tmp/tmp.news_lk.article.%s.html' % (h)
    if os.path.exists(html_file):
        _utils.log.info('Getting html from %s', html_file)
        return html_file

    remote_url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/news_lk.article.%s.html' % h,
    )
    if www.exists(remote_url):
        _utils.log.info('Getting html from %s', remote_url)
        html = www.download(remote_url)
        filex.write(html_file, html)
        return html_file

    _utils.log.info('Downloading html from %s', url)
    html = cached_read(url)
    filex.write(html_file, html)
    _utils.log.info('Wrote %dKB to %s', len(html) / 1000.0, html_file)
    return html_file


def update_summary_file(new_data_list):
    remote_url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/news_lk.latest.summary.tsv',
    )
    summary_file = '/tmp/news_lk.latest.summary.tsv'
    if www.exists(remote_url):
        existing_data_list = www.read_tsv(remote_url)
        _utils.log.info(
            'Downloaded %d articles from %s',
            len(existing_data_list),
            remote_url,
        )
    else:
        _utils.log.warn('No summary file at %s', remote_url)
        existing_data_list = []

    combined_data_list = existing_data_list + new_data_list

    _utils.log.info(
        'Wrote %d entries to %s',
        len(combined_data_list),
        summary_file,
    )
    tsv.write(summary_file, combined_data_list)


def download_and_parse(url):
    url_hash = hashx.md5(url)[:8]
    data_file = '/tmp/news_lk.article.%s.json' % (url_hash)

    if os.path.exists(data_file):
        _utils.log.warn('%s already exists', data_file)
        return None

    remote_url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/news_lk.article.%s.json' % url_hash,
    )
    if www.exists(remote_url):
        _utils.log.warn('%s already exists', remote_url)
        return None

    html_file = download(url)
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
        url_hash=url_hash,
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
    return data


def _scrape():
    link_urls = get_link_urls('https://www.dailymirror.lk/')
    new_data_list = []
    for url in link_urls:
        data = download_and_parse(url)
        if data:
            new_data_list.append(
                {
                    'url_hash': data['url_hash'],
                    'ut': data['ut'],
                    'time_id': data['time_id'],
                    'title': data['title'],
                    'url': data['url'],
                    'n_chars': len('\n'.join(data['paragraphs'])),
                }
            )
        if len(new_data_list) >= MAX_URLS_TO_DOWNLOAD:
            break
    if new_data_list:
        update_summary_file(new_data_list)


if __name__ == '__main__':
    _scrape()
