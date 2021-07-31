import urllib.parse

from bs4 import BeautifulSoup
from utils import timex, www

from news_lk import _utils
from news_lk._utils import log


def scrape(search_text):
    url = 'https://duckduckgo.com/?' + urllib.parse.urlencode(
        {
            'q': search_text,
            't': 'ffab',
            'iar': 'news',
            'df': 'd',
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
        ut = _utils.get_ut(timestamp_str, ut_search)
        article = dict(
            ut=ut,
            url=url,
            title=title,
            snippet=snippet,
        )

        article_list.append(article)
    log.info('Found %d articles', len(article_list))
    return article_list
