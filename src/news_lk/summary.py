import os

from bs4 import BeautifulSoup
from utils import filex, www

from news_lk._utils import log


def get_article_hids():
    url = 'https://github.com/nuuuwan/news_lk/tree/data'
    html = www.read(url)

    soup = BeautifulSoup(html, 'html.parser')
    hids = []
    for a in soup.find_all('a', class_='js-navigation-open Link--primary'):
        href = a.get('href')
        if href[-5:] != '.json':
            continue
        hid = href[-13:-5]
        hids.append(hid)
    log.info('Found %d articles hIDs', len(hids))
    return hids


def get_article(hid):
    url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/news_lk.article.%s.json' % hid,
    )
    return www.read_json(url)


def _build():
    hids = get_article_hids()
    date_id_to_articles = {}
    for hid in hids:
        article = get_article(hid)
        log.info('Got article %s' % hid)
        time_id = article['time_id']
        date_id = time_id[:10]
        if date_id not in date_id_to_articles:
            date_id_to_articles[date_id] = []
        date_id_to_articles[date_id].append(article)

    lines = ['# Summary of Articles']
    sorted_data = reversed(
        sorted(date_id_to_articles.items(), key=lambda x: x[0]),
    )
    for date_id, articles in sorted_data:
        lines.append('## %s' % date_id)
        sorted_articles = reversed(
            sorted(articles, key=lambda article: article['time_id']),
        )
        for article in sorted_articles:
            lines.append(
                '* %s - [%s](%s) (%s)'
                % (
                    article['time_id'][-4:],
                    article['title'],
                    article['url'],
                    article['source'],
                )
            )
    summary_file = '/tmp/news_lk.summary.md'
    filex.write(summary_file, '\n'.join(lines))
    log.info('Wrote summary to %s', summary_file)
