import logging
import os

LOG_FORMAT = '%(asctime)s -- %(message)s'
LOG_LEVEL = logging.DEBUG

PICBEAR_DATE_FORMAT = "%B %d %Y - %H:%M"

DATA_DIR = 'data'

DATE_FORMAT = PICBEAR_DATE_FORMAT

# Relate to reading/writing user CSV/TXT files
USER_POOL_FN = os.path.join(DATA_DIR, 'seed/user_pool.txt')
TOP_USER_FN = os.path.join(DATA_DIR, 'seed/top_users.csv')
SEED_USER_FN = os.path.join(DATA_DIR, 'seed/seed_users{}.csv')
TOP_USER_HEADER = (
    'top_user_date', 'username', 'rank (follower_count)',
    'media_scrape_dt', 'media_url',
    'medadata_scrape', 'likes', 'comments'
)
SEED_USER_HEADER = (
    'username', 'media_scrape_dt', 'media_url',
    'medadata_scrape', 'likes', 'comments'
)

MEDIA_IMAGE = 'image'
MEDIA_VIDEO = 'video'
