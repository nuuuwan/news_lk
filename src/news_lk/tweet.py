"""Tweet."""


from utils import twitter, timex
from news_lk._utils import log

MAX_ARTICLE_AGE = timex.SECONDS_IN.DAY


def tweet_article(article):
    ut = article['ut']
    url_hash = article['url_hash']
    url = article['url']
    ut_now = timex.get_unixtime()
    delta = ut_now - ut
    if delta > MAX_ARTICLE_AGE:
        log.warn('%s: Article too old. Not tweeting', url_hash)
        return False

    tweet_text = '''{snippet}

{url}'''.format(
        snippet=article['snippet'][:100] + '...',
        url=url,
    )
    status_image_files = None
    profile_image_file = None
    banner_image_file = None

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
        profile_image_file=profile_image_file,
        banner_image_file=banner_image_file,
    )


if __name__ == '__main__':
    tweet_article(
        {
            "date": "2021-07-30",
            "title": "Durham bubble breach: Gunathilaka, Mendis and Dickwella suspended from international cricket for one year",
            "source": "www.msn.com",
            "snippet": "Danushka Gunathilaka, Kusal Mendis, and Niroshan Dickwella have all been suspended from international cricket for a year for breaking Sri Lanka's bio-bubble on a night out in Durham last month. They have each also been fined 10 million rupees (USD 50,",
            "url": "https://www.msn.com/en-in/sport/cricket/durham-bubble-breach-gunathilaka-mendis-and-dickwella-suspended-from-international-cricket-for-one-year/ar-AAMKOeL",
            "url_hash": "ef3d8d44981bd5129a072e0cf8bb6161",
            "ut": 1627656635,
            "ent_ids": [
                "PERSON(Danushka Gunathilaka)",
                "PERSON(Kusal Mendis)",
                "PERSON(Niroshan Dickwella)",
                "DATE(a year)",
                "GPE(Sri Lanka's)",
                "TIME(a night)",
                "GPE(Durham)",
                "DATE(last month)",
                "CARDINAL(10 million)",
            ],
        },
    )
