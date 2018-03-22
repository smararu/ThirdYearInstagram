# README #

Some rough-and-ready Python scripts designed to scrape Instagram images.


### Dependancies ###

Requires:

* Chrome
* Python 3
* BeautifulSoup (a package for Python, install using pip)
* selenium (a package for Python, install using pip)

You will also need to create the directory path `data/seed` inside the cloned directory. 


### Quick Start ###

Running `python3 scrape_instagram.py` from the terminal will begin the slow process of scraping a fair quantity of data from Instagram mirror <http://picbear.com>.


### For more fine-grained control ###

To get the top 100 users:
```python
from instagram.users import top_users
top_100_most_followed = top_users()
```

To seed random users based on those top users:
```python
from instagram.users import seed_users
user_pool = seed_users(top_100_most_followed)
```

To get a user's media items:
```python
from instagram.media import get_media

username = user_pool[0]

# The ten most recent
(dt, images, videos) = get_media(username, n=10)

# All items
(dt, images, videos) = get_media(username)
```

To get metadata for a media item:
```python
from instagram.media import get_metadata

for (dt, cdn_url, picbear_url) in images:
    (poll_dt, share_dt, caption, likes, comments, *tmp) = get_metadata(picbear_url)
```