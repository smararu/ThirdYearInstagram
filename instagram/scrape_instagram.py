# Standard library imports
import csv
from datetime import datetime
import os.path
import logging
import sys

# Local imports
from instagram.const import DATE_FORMAT, DATA_DIR, USER_POOL_FN
from instagram.error import HTTPRetreivalError, UnexpectedResult
from instagram.media import get_media, get_metadata
from instagram.users import (
    is_private_account, seed_users as _init_seed_users,
    top_users as _init_top_users
)
from instagram.web import is_server_error


server_errors = 0
SERVER_ERR_LIMIT = 2
SERVER_ERR_MSG = 'Max number of consecutive server errors reached. '
SERVER_ERR_MSG += 'Server may be blocking traffic. Try again later.'


def init_user_pool():
    LOG_MSG = 'init_user_pool: {msg} [len(user_pool)={len}]'
    if not os.path.exists(USER_POOL_FN):
        top_users = _init_top_users()

        # Just do one level of abstraction from the top users
        user_pool = _init_seed_users(top_users)
        logging.debug(LOG_MSG.format(
            msg='dropping private users', len=len(user_pool)
        ))
        user_pool = [u for u in user_pool if not is_private_account(u)]

        with open(USER_POOL_FN, 'w') as file:
            logging.debug(LOG_MSG.format(
                msg='writing {}'.format(USER_POOL_FN), len=len(user_pool)
            ))
            for user in user_pool:
                file.write("{}\n".format(user))
    else:
        user_pool = list()
        with open(USER_POOL_FN, 'r') as file:
            for line in file:
                user_pool.append(line.strip())

    return user_pool


def create_user_file(user, fn):
    logging.debug('create_user_file: IN')
    (dt, images, videos) = get_media(uname)  # Raises Exception
    with open(csvfile, 'w', newline='') as fh:
        csv_file = csv.writer(fh, delimiter=',')
        header = ("user_poll_dt", "content_url", "picbear_url")
        csv_file.writerow(header)
        for media_item in images + videos:
            args = [datetime.strftime(dt, DATE_FORMAT)] + list(media_item)
            csv_file.writerow(args)


def extend_media_data(row):
    (dt, media_url, picbear_url) = row
    (poll_dt, share_dt, caption, likes, comments, *tmp) = get_metadata(
        picbear_url
    )
    return (
        dt, media_url, picbear_url, datetime.strftime(poll_dt, DATE_FORMAT),
        datetime.strftime(share_dt, DATE_FORMAT), caption, likes, comments
    )


if __name__ == '__main__':
    user_pool = init_user_pool()

    for (i, uname) in enumerate(user_pool):
        pre = "Processing user {}".format(i+1)
        logging.debug("{}/{}    [{}]".format(
            pre, len(user_pool), uname
        ))
        csvfile = os.path.join(DATA_DIR, '{}.csv'.format(uname))
        if os.path.exists(csvfile):
            logging.debug('{}: csvfile already exists'.format(pre))
        else:
            logging.debug('{}: csvfile does not exist'.format(pre))
            try:
                prev_err_count = server_errors
                create_user_file(uname, csvfile)
                server_errors = 0
            except HTTPRetreivalError as e:
                msg = "{}: could not fetch user data ".format(pre)
                msg += "(HTTPRetreivalError{0}).".format(
                    '' if not hasattr(e, 'code') else ' {0}'.format(e.code)
                )
                if is_server_error(e):
                    server_errors += 1
                    if server_errors >= SERVER_ERR_LIMIT:
                        sys.exit(SERVER_ERR_MSG)
                msg += "Skipping..."
                logging.debug(msg)
                logging.debug(e)
                continue

        mod = False
        new_data = list()
        with open(csvfile, 'r', newline='') as fh:
            csv_file = csv.reader(fh, delimiter=',')
            for orig_row in csv_file:
                if orig_row[2] == "picbear_url":
                    new_data.append((
                        "user_poll_dt", "content_url", "picbear_url",
                        "media_poll_dt", "media_share_dt", "caption",
                        "likes", "comments"
                    ))
                elif len(orig_row) <= 3 or not orig_row[3]:
                    row = orig_row[:3] if len(orig_row) > 2 else orig_row[:]
                    try:
                        logging.debug("{}: extending media data.".format(pre))
                        row = extend_media_data(row)
                        mod = True
                        server_errors = 0
                    except (UnexpectedResult, HTTPRetreivalError) as e:
                        msg = "{}: could not fetch metadata ({}).".format(
                            pre, e.__class__.__name__
                        )
                        msg = msg.format('' if not hasattr(
                            e, 'code'
                        ) else ' {0}'.format(e.code))
                        if is_server_error(e):
                            server_errors += 1
                            if server_errors >= SERVER_ERR_LIMIT:
                                sys.exit(SERVER_ERR_MSG)
                        msg += "Skipping..."
                        logging.debug(msg)
                        logging.debug(e)
                        new_data.append(orig_row)
                    new_data.append(row)
                else:
                    new_data.append(orig_row)

            if not mod:
                continue

            with open(csvfile, 'w', newline='', encoding='utf-8') as fh:
                csv_file = csv.writer(fh, delimiter=',')
                for row in new_data:
                    csv_file.writerow(row)
