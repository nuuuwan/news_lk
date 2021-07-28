import os

from utils import hashx, timex, tsv, www

from news_lk import scrape_dailymirror, scrape_duckduckgo
from news_lk._utils import log

DATA_FILE_NAME_ONLY = 'news_lk.summary.tsv'


def expand_new_article(article):
    url = article['url']
    article['url_hash'] = hashx.md5(url)
    article['date_id'] = timex.format_time(article['ut'], '%Y-%m-%d')

    source = url.partition('//')[2].partition('/')[0]
    article['source'] = source

    return article


def expand_article(article):
    return {
        'date_id': article['date_id'],
        'title': article['title'],
        'source': article['source'],
        'snippet': article['snippet'],
        
        'url': article['url'],
        'url_hash': article['url_hash'],
        'ut': article['ut'],
    }


def get_new_articles():
    new_article_list = scrape_duckduckgo.scrape() + scrape_dailymirror.scrape()
    new_article_list = list(map(expand_new_article, new_article_list))
    return new_article_list


def get_existing_articles():
    url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/%s' % DATA_FILE_NAME_ONLY,
    )
    if not www.exists(url, timeout=5):
        return []
    return www.read_tsv(url)


def scrape_and_dump():
    new_article_list = get_new_articles()
    log.info('Got %d new articles', len(new_article_list))

    existing_article_list = get_existing_articles()
    log.info('Got %d existing articles', len(existing_article_list))

    # dedupe
    url_hash_to_article = {}
    for article in new_article_list + existing_article_list:
        url_hash_to_article[article['url_hash']] = article
    deduped_article_list = sorted(
        url_hash_to_article.values(),
        key=lambda article: -(int)(article['ut']),
    )
    log.info('Got %d combined articles', len(deduped_article_list))

    deduped_article_list = list(map(expand_article, deduped_article_list))

    data_file = '/tmp/%s' % DATA_FILE_NAME_ONLY
    tsv.write(data_file, deduped_article_list)
    log.info('Wrote %d articles to %s', len(deduped_article_list), data_file)


if __name__ == '__main__':
    scrape_and_dump()
