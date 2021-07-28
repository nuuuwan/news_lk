"""Uploaded data to nuuuwan/news_lk:data branch."""

from news_lk import scrape

if __name__ == '__main__':
    scrape.scrape_and_dump()
