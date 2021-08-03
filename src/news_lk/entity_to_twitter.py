import os

from utils import jsonx, timex, www

from news_lk import scrape
from news_lk._utils import log


def get_entity_to_twitter_map(time_id):
    file_only = 'news_lk.entity_to_twitter_map.%s.json' % time_id
    remote_url = os.path.join(
        'https://raw.githubusercontent.com',
        'nuuuwan/news_lk/data/%s' % file_only,
    )
    entity_to_twitter_map = {}
    if www.exists(remote_url, timeout=5):
        entity_to_twitter_map = www.read_json(remote_url)
    log.info(
        'Got entity_to_twitter_map with %d entries from %s',
        len(entity_to_twitter_map.keys()),
        remote_url,
    )
    return entity_to_twitter_map


def build(date_list, current_time_id=None):

    entity_to_twitter_map = get_entity_to_twitter_map(current_time_id)

    entity_text_set = set()
    for date in date_list:
        article_list = scrape.get_date_article_list(date)
        for article in article_list:
            for ent_info in article['ent_info_list']:
                text = ent_info['text']
                label = ent_info['label']

                if label in ['PERSON', 'NORP', 'GPE', 'ORG']:
                    if 'the ' == text[:4].lower():
                        text = text[4:]
                    entity_text_set.add(text)

    time_id = timex.format_time(timex.get_unixtime(), '%Y-%m-%d-%H%M')
    entity_to_twitter_map['--- %s ---' % time_id] = None
    for entity_text in sorted(entity_text_set):
        if entity_text not in entity_to_twitter_map:
            entity_to_twitter_map[entity_text] = None

    map_file = '/tmp/news_lk.entity_to_twitter_map.%s.json' % (time_id)
    jsonx.write(map_file, entity_to_twitter_map)
    log.info(
        'Wrote %d map entries to %s',
        len(entity_to_twitter_map.keys()),
        map_file,
    )


if __name__ == '__main__':
    DATE_LIST = [
        '2021-08-03',
        '2021-08-02',
        '2021-08-01',
        '2021-07-31',
        '2021-07-30',
        '2021-07-29',
        '2021-07-28',
    ]
    CURRENT_TIME_ID = None
    build(DATE_LIST, CURRENT_TIME_ID)
