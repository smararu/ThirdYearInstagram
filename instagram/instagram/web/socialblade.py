# Standard library imports
import datetime
import random

# Third party imports
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# Local imports
from .util import make_request


SOCIALBLADE = "https://socialblade.com/instagram/top/100/followers"


def _cached_n_users(n):
    cache_date = datetime.date(2017, 5, 17)
    cached_users = [
        {'user': 'instagram', 'rank': 1, 'followers': 223409759},
        {'user': 'selenagomez', 'rank': 2, 'followers': 120477155},
        {'user': 'arianagrande', 'rank': 3, 'followers': 105568191},
        {'user': 'taylorswift', 'rank': 4, 'followers': 102112309},
        {'user': 'beyonce', 'rank': 5, 'followers': 101943380},
        {'user': 'cristiano', 'rank': 6, 'followers': 101325101},
        {'user': 'kimkardashian', 'rank': 7, 'followers': 99875050},
        {'user': 'kyliejenner', 'rank': 8, 'followers': 93724590},
        {'user': 'justinbieber', 'rank': 9, 'followers': 86896137},
        {'user': 'therock', 'rank': 10, 'followers': 86631981},
    ]
    if n > len(cached_users):
        raise ValueError('User n is too large: insufficient cached users')
    return (cache_date, cached_users[:n])


def _parse_socialblade_content(parsed_html):
    most_followed = list()
    table = parsed_html.find(
        "div", attrs={"class": "content-module-wide"}
    )
    if not table:
        return None
    record = dict()
    for (i, val) in enumerate(
        table.find_all_next("div", attrs={"class": "table-cell"})
    ):
        case = i % 6
        if case not in (0, 2, 4, 5):
            continue
        data = val.contents[0]
        if case is 0:
            record['rank'] = int(data)
        elif case is 2:
            record['user'] = data.contents[0]
        elif case is 4:
            record['followers'] = int(''.join([c for c in data if c != ',']))
        elif case is 5:
            most_followed.append(record)
            record = dict()
    return most_followed


def top_n_followed_users(n=100):
    parsed_html = make_request(SOCIALBLADE, delay=False)
    if parsed_html:
        most_followed = _parse_socialblade_content(parsed_html)
    else:
        print('Warning - top_n_users() using cached data.')
        return _cached_n_users(n)

    if n > len(most_followed):
        raise ValueError('User n is too large')

    return (datetime.date.today(), most_followed[:n])


def random_popular_users(n=10, pool_size=100):
    if n >= pool_size:
        raise ValueError('n must be smaller than pool_size')
    (seed_date, seed) = top_n_followed_users(pool_size)
    random.shuffle(seed)
    return (seed_date, seed[:n])
