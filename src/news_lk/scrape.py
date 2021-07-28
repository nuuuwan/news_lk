import os

import spacy
from utils import filex, hashx, jsonx, timex, www

from news_lk import scrape_dailymirror, scrape_duckduckgo
from news_lk._utils import log

nlp = spacy.load("en_core_web_sm")


def expand_article_basic(article):
    url = article['url']
    article['url_hash'] = hashx.md5(url)
    article['date'] = timex.format_time(article['ut'], '%Y-%m-%d')
    return article


def expand_article(article):
    url = article['url']
    source = url.partition('//')[2].partition('/')[0]
    article['source'] = source

    doc = nlp(article['snippet'])
    ent_ids = []
    for ent in doc.ents:
        ent_id = '%s(%s)' % (ent.label_, ent.text)
        ent_ids.append(ent_id)
    log.info(
        'Extracted %d ents from %s',
        len(ent_ids),
        url,
    )
    article['ent_ids'] = ent_ids

    return {
        'date': article['date'],
        'title': article['title'],
        'source': article['source'],
        'snippet': article['snippet'],
        'url': article['url'],
        'url_hash': article['url_hash'],
        'ut': article['ut'],
        'ent_ids': article['ent_ids'],
    }


def get_new_articles():
    new_article_list = scrape_duckduckgo.scrape() + scrape_dailymirror.scrape()
    return new_article_list


def scrape_and_dump():
    new_article_list = get_new_articles()
    log.info('Got %d new articles', len(new_article_list))
    new_article_list = list(map(expand_article_basic, new_article_list))

    # group by date, dump and dump
    date_to_hash_to_article = {}
    for article in new_article_list:
        date = article['date']
        url_hash = article['url_hash']
        if date not in date_to_hash_to_article:
            date_to_hash_to_article[date] = {}
        date_to_hash_to_article[date][url_hash] = article

    summary_stats_list = []
    for date in date_to_hash_to_article:
        file_only = 'news_lk.%s.json' % date

        remote_url = os.path.join(
            'https://raw.githubusercontent.com',
            'nuuuwan/news_lk/data/%s' % file_only,
        )
        existing_article_list = []
        if www.exists(remote_url, timeout=5):
            existing_article_list = www.read_json(remote_url)

        existing_article_hashes = list(
            map(
                lambda d: d['url_hash'],
                existing_article_list,
            )
        )
        upload_article_list = existing_article_list
        for hash, article in date_to_hash_to_article[date].items():
            if hash in existing_article_hashes:
                continue
            upload_article_list.append(expand_article(article))

        data_file = '/tmp/%s' % file_only
        jsonx.write(data_file, upload_article_list)
        n_articles = len(upload_article_list)
        log.info(
            'Wrote %d articles to %s',
            n_articles,
            data_file,
        )

        summary_stats_list.append(
            {
                'date': date,
                'n_articles': n_articles,
            }
        )
    summary_stats_list = sorted(summary_stats_list, key=lambda d: d['date'])
    base_url = 'https://github.com/nuuuwan/news_lk/blob/data'
    lines = ['# Summary']
    for d in summary_stats_list:
        date = d['date']
        file_only = 'news_lk.%s.json' % date
        line = '* [%s](%s) (%d articles)' % (
            date,
            '%s/%s' % (base_url, file_only),
            d['n_articles'],
        )
        lines.append(line)

    time_str = timex.format_time(timex.get_unixtime(), '%I:%M%p, %B %d, %Y')
    lines += [
        '',
        '*Generated at %s*' % time_str,
    ]
    summary_file_name = '/tmp/README.md'
    filex.write(summary_file_name, '\n'.join(lines))
    log.info(
        'Wrote summary for %d days to %s',
        len(summary_stats_list),
        summary_file_name,
    )


if __name__ == '__main__':
    scrape_and_dump()
