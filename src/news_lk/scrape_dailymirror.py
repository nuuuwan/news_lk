from bs4 import BeautifulSoup
from utils import timex, www

from news_lk import _utils
from news_lk._utils import log


def scrape():
    url = 'https://www.dailymirror.lk/latest-news/108'
    html = www.read(url, use_selenium=True)
    soup = BeautifulSoup(html, 'html.parser')

    ut_search = timex.get_unixtime()
    article_list = []
    for div in soup.find_all('div', class_='lineg'):
        a_url = div.find('a')
        url = a_url.get('href')

        h3_title = div.find('h3')
        title = h3_title.text

        ps = div.find_all('p')
        p_snippet = ps[1]
        snippet = p_snippet.text

        span_timestamp = div.find('span', class_='gtime')
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


if __name__ == '__main__':
    scrape()
