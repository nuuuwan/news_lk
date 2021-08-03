"""Tweet."""

from utils import timex, twitter

from news_lk import _utils, entity_to_twitter
from news_lk._utils import log

MAX_ARTICLE_AGE = timex.SECONDS_IN.DAY
MAX_SNIPPET_LENGTH = 200
TWEETING_ENABLED = False

ENTITY_TO_TWITTER_MAP_TIME_ID = None
ENTITY_TO_TWITTER_MAP = entity_to_twitter.get_entity_to_twitter_map(
    ENTITY_TO_TWITTER_MAP_TIME_ID
)


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

    for before, after in ENTITY_TO_TWITTER_MAP.items():
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
    _utils.random_sleep()
