"""Uploaded data to nuuuwan/news_lk:data branch."""

import os


def upload_data():
    """Upload data."""
    os.system('echo "test data" > /tmp/news_lk.test.txt')
    os.system('echo "# news_lk" > /tmp/README.md')


if __name__ == '__main__':
    upload_data()
