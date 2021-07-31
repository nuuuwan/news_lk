import os

import spacy
from utils import filex, hashx, jsonx, timex, www

from news_lk import scrape_duckduckgo, tweet
from news_lk._utils import log

nlp = spacy.load("en_core_web_sm")

SEARCH_TEXT_LIST = [
    'Sri Lanka Daily Mirror',
    'Sri Lanka Daily News',
    'Sri Lanka Island',
    'Sri Lanka Ada Derana',
    'Sri Lanka Associated Press',
    'Sri Lanka FT',
    'Sri Lanka EconomyNext',
    'Sri Lanka Colombo Gazette',
    'Sri Lanka Colombo Page',
]


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
    ent_info_list = []
    for ent in doc.ents:
        ent_info = {
            'label': ent.label_,
            'text': ent.text,
            'start_end': [ent.start, ent.end],
        }
        ent_info_list.append(ent_info)
    log.info(
        'Extracted %d ents from %s',
        len(ent_info_list),
        url,
    )
    article['ent_info_list'] = ent_info_list

    return {
        'date': article['date'],
        'title': article['title'],
        'source': article['source'],
        'snippet': article['snippet'],
        'url': article['url'],
        'url_hash': article['url_hash'],
        'ut': article['ut'],
        'ent_info_list': article['ent_info_list'],
    }


def get_new_articles():
    new_article_list = []
    for search_text in SEARCH_TEXT_LIST:
        new_article_list += scrape_duckduckgo.scrape(search_text)
    return new_article_list


def scrape_and_dump():
    new_article_list = get_new_articles()
    log.info('Got %d new articles', len(new_article_list))
    new_article_list = list(map(expand_article_basic, new_article_list))

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
            expanded_new_article = expand_article(article)
            tweet.tweet_article(expanded_new_article)
            upload_article_list.append(expanded_new_article)

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
    lines = ['# Summary', '*Latest scrapes*']
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
