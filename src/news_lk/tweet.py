"""Tweet."""
import time
import random
import re
from utils import twitter, timex
from news_lk._utils import log

MAX_ARTICLE_AGE = timex.SECONDS_IN.DAY
MAX_SNIPPET_LENGTH = 200
TWEETING_ENABLED = False

ENT_TEXT_TO_TWITTER = {}


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
    for ent_info in article['ent_info_list']:
        text = ent_info['text']
        label = ent_info['label']
        if text in ENT_TEXT_TO_TWITTER:
            twitter_text = ENT_TEXT_TO_TWITTER[text]
            snippet = snippet.replace(text, twitter_text)
        if label in ['PERSON']:
            twitter_text = '#' + re.sub(r'[^a-zA-Z0-9]', '', text)
            snippet = snippet.replace(text, twitter_text)

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
    time.sleep(random.random() + 1)


if __name__ == '__main__':
    tweet_article(
        {
            "date": "2021-07-30",
            "title": "Sivaji Ganesan was a World class Actor",
            "source": "www.dailymirror.lk",
            "snippet": "Sivaji Ganesan, M.G. Ramachandran (MGR) and Gemini Ganesan comprised the triumvirate that dominated Tamil cinema in India from the fifties to the seventies of the 20th century. ..",
            "url": "https://www.dailymirror.lk/recomended-news/Sivaji-Ganesan-was-a-World-class-Actor/277-217263",
            "url_hash": "af48f05c6b1aa66a4a323aa07a081b9a",
            "ut": 1627676364,
            "ent_info_list": [
                {
                    "label": "PERSON",
                    "text": "Sivaji Ganesan",
                    "start_end": [0, 2],
                },
                {
                    "label": "PERSON",
                    "text": "M.G. Ramachandran",
                    "start_end": [3, 5],
                },
                {"label": "ORG", "text": "MGR", "start_end": [6, 7]},
                {
                    "label": "PERSON",
                    "text": "Gemini Ganesan",
                    "start_end": [9, 11],
                },
                {"label": "GPE", "text": "Tamil", "start_end": [16, 17]},
                {"label": "GPE", "text": "India", "start_end": [19, 20]},
                {
                    "label": "DATE",
                    "text": "the fifties",
                    "start_end": [21, 23],
                },
                {
                    "label": "DATE",
                    "text": "the seventies of the 20th century",
                    "start_end": [24, 30],
                },
            ],
        },
    )
