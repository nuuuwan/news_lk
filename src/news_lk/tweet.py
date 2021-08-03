"""Tweet."""
import random
import re
import time

from utils import timex, twitter

from news_lk._utils import log

MAX_ARTICLE_AGE = timex.SECONDS_IN.DAY
MAX_SNIPPET_LENGTH = 200
TWEETING_ENABLED = False
MEAN_SLEEP_TIME = 5

ENT_TEXT_TO_TWITTER = {
    'Sri Lanka': '#SriLanka🇱🇰',
    'Rishad Bathiudeen': '@rbathiudeen',
    'Kotelawala National Defense University': '@Kotelawala_uni',
    'COVID-19': '#COVID19',
}


def random_sleep():
    time.sleep(random.random() * MEAN_SLEEP_TIME)


def tweet_article(article):
    ut = article['ut']
    url_hash = article['url_hash']
    url = article['url']
    ut_now = timex.get_unixtime()
    delta = ut_now - ut
    if delta > MAX_ARTICLE_AGE:
        log.warn('%s: Article too old. Not tweeting', url_hash)
        return False

    snippet = article['snippet']

    # transform
    replace_map = ENT_TEXT_TO_TWITTER
    for ent_info in article['ent_info_list']:
        text = ent_info['text']
        label = ent_info['label']

        if text not in replace_map:
            if label in ['PERSON', 'NORP', 'GPE', 'ORG']:
                if text in ENT_TEXT_TO_TWITTER:
                    twitter_text = ENT_TEXT_TO_TWITTER[text]
                else:
                    log.warn("    '%s': '%s', ", text, text)
                    twitter_text = '#' + re.sub(r'[^a-zA-Z0-9]', '', text)
                replace_map[text] = twitter_text

    for before, after in replace_map.items():
        snippet = snippet.replace(before, after)

    if len(snippet) > MAX_SNIPPET_LENGTH:
        snippet = snippet[:MAX_SNIPPET_LENGTH] + '...'

    tweet_text = '''{snippet}

{url}'''.format(
        snippet=snippet,
        url=url,
    )
    status_image_files = None
    profile_image_file = None
    banner_image_file = None

    if not TWEETING_ENABLED:
        log.warn('TWEETING_ENABLED = %s', str(TWEETING_ENABLED))
        return False

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
        profile_image_file=profile_image_file,
        banner_image_file=banner_image_file,
    )
    random_sleep()
