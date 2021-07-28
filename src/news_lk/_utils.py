"""Utils."""

import logging

from utils import timex

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('news_lk')


def get_ut(timestamp_str, ut_cur=None):
    timestamp_str = timestamp_str.strip()
    q_str, unit, suffix = timestamp_str.split(' ')

    if ut_cur is None:
        ut_cur = timex.get_unixtime()

    if suffix == 'ago':  # relative time
        q = (int)(q_str)
        unit = unit.lower()
        if 'second' in unit:
            delta = q
        elif 'minute' in unit:
            delta = q * timex.SECONDS_IN.MINUTE
        elif 'hour' in unit:
            delta = q * timex.SECONDS_IN.HOUR
        elif 'day' in unit:
            delta = q * timex.SECONDS_IN.DAY
        elif 'week' in unit:
            delta = q * timex.SECONDS_IN.WEEK
        else:
            delta = 0
            log.warn('Unknown timestamp_str: %s'.timestamp_str)
        return ut_cur - delta
    else:  # absolute time
        return timex.parse_time(timestamp_str, '%d %b %Y')
