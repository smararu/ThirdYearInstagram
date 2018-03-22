# Standard library imports
import logging
import random
import ssl
import sys
import time
from urllib import error, request

# Third party imports
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from selenium import webdriver


def is_server_error(e):
    return hasattr(e, 'code') and e.code < 600 and e.code > 499


def make_request(url, delay=True):
    if delay:
        random_delay()
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        req = request.Request(url, headers={'User-Agent': "A Browser"})
        fp = request.urlopen(req)
    except error.URLError:
        print("Static request error:", sys.exc_info()[0])
        raise
    return BeautifulSoup(fp, "html.parser")


def make_scrolling_request(url):
    parsed_html = None
    browser = webdriver.Chrome('./chromedriver')
    browser.get(url)
    try:
        last_height = browser.execute_script(
            "return document.body.scrollHeight"
        )
        flag = 0
        while True:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            random_delay(min=0.4, max=0.7)  # seconds
            new_height = browser.execute_script(
                "return document.body.scrollHeight"
            )
            if new_height == last_height:
                if flag > 2:
                    break
                flag += 1
            else:
                last_height = new_height
                flag = 0
    except Exception:  # :(
        print("Scrolling request error:", sys.exc_info()[0])
        raise
    else:
        html_source = browser.page_source
        parsed_html = BeautifulSoup(html_source, "html.parser")
    finally:
        random_delay(min=0.2, max=0.6)
        browser.quit()
        random_delay(min=0.25, max=0.4)
    return parsed_html


def random_delay(min=0.2, max=0.45):  # min and max unit is seconds, max 2 DP
    multiplier = 100
    int_min = int(min*multiplier)
    int_max = int(max*multiplier)
    logging.debug('random_delay(): sleeping...')
    time.sleep(random.randrange(int_min, int_max)/multiplier)
    logging.debug('random_delay(): done.')
