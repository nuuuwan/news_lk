import urllib.parse

from _utils import log
from bs4 import BeautifulSoup
from utils import hashx, timex, www


def get_time_delta(timestamp_str):
    q_str, unit, _ = timestamp_str.split(' ')
    q = (int)(q_str)
    if 'second' in unit:
        return q
    if 'minute' in unit:
        return q * timex.SECONDS_IN.MINUTE
    if 'hour' in unit:
        return q * timex.SECONDS_IN.HOUR
    if 'day' in unit:
        return q * timex.SECONDS_IN.DAY
    if 'week' in unit:
        return q * timex.SECONDS_IN.WEEK

    log.warn('Unknown timestamp_str: %s'.timestamp_str)
    return 0


def scrape():
    url = 'https://duckduckgo.com/?' + urllib.parse.urlencode(
        {
            'q': 'Sri Lanka',
            't': 'ffab',
            'iar': 'news',
            'df': 'w',
            'ia': 'news',
        }
    )
    html = www.read(url, use_selenium=True)
    soup = BeautifulSoup(html, 'html.parser')

    ut_search = timex.get_unixtime()
    article_list = []
    for div in soup.find_all('div', class_='result__body'):
        a_url = div.find('a', class_='result__a')
        url = a_url.get('href')
        title = a_url.text

        div_snippet = div.find('div', class_='result__snippet')
        snippet = div_snippet.text

        span_timestamp = div.find('span', class_='result__timestamp')
        timestamp_str = span_timestamp.text
        time_delta = get_time_delta(timestamp_str)
        ut = ut_search - time_delta
        time_id = timex.format_time(ut, '%Y-%m-%d %H:%M:%S')

        h_id = hashx.md5(url)

        article = dict(
            h_id=h_id,
            time_id=time_id,
            ut=ut,
            url=url,
            title=title,
            snippet=snippet,
        )
        print(article)

        article_list.append(article)
    log.info('Found %d articles', len(article_list))
    return article_list


if __name__ == '__main__':
    scrape()
