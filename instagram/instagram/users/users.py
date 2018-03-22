# Standard library imports
import csv
import logging
import os
import random
import sys

# Local imports
from ..const import (
    LOG_FORMAT, LOG_LEVEL, SEED_USER_FN, SEED_USER_HEADER, TOP_USER_FN,
    TOP_USER_HEADER
)
from ..web.picbear import get_media, get_metadata
from ..web.socialblade import top_n_followed_users as top_100_followed_users
from ..error import PrivateAccountError


log = logging.getLogger()
log.setLevel(LOG_LEVEL)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter(LOG_FORMAT)
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)


def top_users(filename=TOP_USER_FN):
    if not os.path.exists(filename):
        top_users = get_top_user_interactors()
    else:
        logging.debug("Using existing top_user file: {}".format(filename))
        top_users = read_seed_usernames_from_csv(filename)
    return top_users


def seed_users(parent_seed_users, level=None, filename=SEED_USER_FN):
    filename = filename.format(level if level else '')
    if not os.path.exists(filename):
        seed_users = get_seed_user_interactors(parent_seed_users)
    else:
        logging.debug("Using existing seed_user file: {}".format(filename))
        seed_users = read_seed_usernames_from_csv(filename)
    return seed_users


def read_seed_usernames_from_csv(filename):
    seed_users = list()
    with open(filename, 'r') as fh:
        csv_file = csv.reader(fh, delimiter=',')
        idx_uname = None
        for row in csv_file:
            if idx_uname is None:
                idx_uname = row.index('username')
                continue
            seed_users.append(row[idx_uname])
    return seed_users


def get_interactors(username, num_posts=10):
    logging.debug("get_interactors('{}', num_posts={})".format(
        username, num_posts
    ))
    media_searched = list()

    # Get the specified users most recent posts
    (media_dt, images, videos) = get_media(username, n=num_posts)

    # Extract likes and comments - note that picbear only lists a max of the
    # **most recent** 10 comments and 15 likes (and some comments may be from
    # the same commenter) meaning that the max length of these two lists is 10
    # and 15 respectively.
    interactors = list()
    for (tmp, picbear_url) in images + videos:
        (metadata_dt, *tmp, likes, comments) = get_metadata(picbear_url)
        media_searched.append(
            # media_dt - when the media was scraped from the user's homepage
            # metadata_dt - when the list of likes/comments was scraped
            (media_dt, picbear_url, metadata_dt, likes, comments)
        )   
        interactors += likes + comments
    interactors = list(set(interactors))
    random.shuffle(interactors)             # len is max 250, but probably less
    return (interactors, media_searched)


def get_seed_user_interactors(
    seed_users, num_users=100, num_posts=10, write_csv=SEED_USER_FN, level=None
):
    seed_media = list()
    interacting_users = list()
    n = 0
    for username in seed_users:
        logging.debug("seed_users, n={}".format(n))
        if n is num_users:
            break

        # Get interacting users
        try:
            (interactors, media_searched) = get_interactors(
                username, num_posts
            )
        except PrivateAccountError:
            continue
        interacting_users.extend(interactors)
        n += 1

        # Keep a record of what was done that we'll later write to csv
        for media in media_searched:
            seed_media.append((username, *media))

    if write_csv:
        csv_file = write_csv.format(level if level else '')
        write_seed_users_csv(seed_media, csv_file)

    return interacting_users


def write_seed_users_csv(seed_media, filename, top_users=False):
    header = TOP_USER_HEADER if top_users else SEED_USER_HEADER

    with open(filename, 'w', newline='') as fh:
        csv_file = csv.writer(fh, delimiter=',')
        csv_file.writerow(header)
        for media in seed_media:
            csv_file.writerow(media)


def get_top_user_interactors(num_posts=10, write_csv=TOP_USER_FN):
    (seed_date, seed_users) = top_100_followed_users(n=5)
    seed_media = list()
    interacting_users = list()
    for (i, user) in enumerate(seed_users):
        # Get interacting users
        username = user['user']
        if i % 10 is 0:
            logging.debug("top_user progress report: user #{}".format(i+1))
        (interactors, media_searched) = get_interactors(username, num_posts)
        interacting_users.extend(interactors)

        # Keep a record of what was done that we'll later write to csv
        for media in media_searched:
            seed_media.append((
                seed_date, username,
                "{r} ({f})".format(r=user['rank'], f=user['followers']),
                *media
            ))

    logging.debug(
        "************ TOP USER INTERACTORS (n={}) ************".format(
            len(interacting_users)
        )
    )

    if write_csv:
        write_seed_users_csv(seed_media, write_csv, top_users=True)

    return interacting_users


if __name__ == '__main__':
    top_users = get_top_user_interactors()

    # Just do one level of abstraction from the top users
    user_pool = get_seed_user_interactors(top_users)

    # Do >1 level of abstraction from the top users
    lv1 = get_seed_user_interactors(top_users, level=1)
    user_pool = get_seed_user_interactors(lv1, level=2)
