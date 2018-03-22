# Standard library
from datetime import datetime
from urllib import error as urlliberror
import logging
import sys

# Third party
from bs4.element import Tag

# Local imports
from .util import make_request, make_scrolling_request
from ..const import MEDIA_IMAGE, MEDIA_VIDEO, PICBEAR_DATE_FORMAT
from ..error import HTTPRetreivalError, PrivateAccountError, UnexpectedResult

URL = "http://picbear.com/{uname}"


def _extract_picbear_media(parsed_html):
    ads = parsed_html.find_all(
        "div", attrs={"class": "grid-media grid-media-ad"}
    )
    media = parsed_html.find_all(
        "div", attrs={"class": "grid-media"}
    )
    return [item for item in media if item not in ads]


def _extract_picbear_mediatype(div):
    media = div.find(
        "a", attrs={"class": "grid-media-media media-detail"}
    )
    picbear_src = media.get("href")

    nested_tags = [child for child in media.contents if isinstance(child, Tag)]
    media_type = MEDIA_VIDEO if 'i' in [
        t.name for t in nested_tags
    ] else MEDIA_IMAGE
    assert(len(nested_tags) is 2 if media_type == MEDIA_VIDEO else 1)
    img_src = nested_tags[0].get('src')

    return (media_type, img_src, picbear_src)


def _extract_media_from_picbear(parsed_html, n=-1):
    divs = _extract_picbear_media(parsed_html)
    images = list()
    videos = list()
    for (i, div) in enumerate(divs):
        if n > 0 and i >= n:
            break
        (media_type, media_src, picbear_src) = _extract_picbear_mediatype(div)
        lst = images if media_type == MEDIA_IMAGE else videos
        lst.append((media_src, picbear_src))
    return (images, videos)


###################################################################
# This is quite ugly, but deliberate. We need to figure out how
# many images picbear shows on a single non-scrolling opening of
# a user's Instagram profile.
###################################################################
try:
    parsed_html = make_request(
        URL.format(uname='arianagrande')  # Someone with plenty of posts
    )
except urlliberror.URLError as e:
    sys.exit("Network Error: check connection and try again\n{0}".format(e))
(images, videos) = _extract_media_from_picbear(parsed_html)
_PICBEAR_DEFAULT_PAGELOAD = len(images) + len(videos)
###################################################################


def _extract_datetimestr_from_picbear(parsed_html):
    dt = parsed_html.find(
        "p", attrs={"class": "media-single-calendar"}
    ).contents
    assert len(dt) is 1 and isinstance(dt[0], str)
    return dt[0]


def _extract_caption_from_picbear(parsed_html):
    caption = parsed_html.find(
        "div", attrs={"class": "media-caption"}
    ).contents
    caption = ' '.join([str(c).strip() for c in caption]).strip()
    return caption


def _extract_likescomments_count_from_picbear(parent_tag, like_or_com):
    count = [e for e in parent_tag.find("h3").contents if isinstance(e, str)]
    assert len(count) is 1
    count = count[0].strip(' ')[:-len(' {}'.format(like_or_com))]
    count = int(''.join([c for c in count if c != ',']))
    return count


def _extract_likescomments_usernames_from_picbear(parent_tag):
    rtn = list()
    for user in parent_tag.find_all("a"):
        rtn.append(user['title'])
    return list(set(rtn))


def _extract_likescomments_from_picbear(parsed_html, like_or_com='comments'):
    if like_or_com.lower() not in ('likes', 'comments'):
        raise ValueError('like_or_com should have value "likes" or "comments"')
    parent = parsed_html.find(
        "div", attrs={"class": "media-{}".format(like_or_com)}
    )
    count = _extract_likescomments_count_from_picbear(parent, like_or_com)
    usernames = (
        _extract_likescomments_usernames_from_picbear(parent)
        if count else list()
    )

    # Note - usernames contains max of the *most recent* 10(comments)/15(likes)
    # ... may be fewer commenters if they've commented >1ce recently
    return (count, usernames)


def is_private_account(user=None, parsed_html=None):
    
    if user and parsed_html:
        raise ValueError("Supply ONE of either 'user' or 'parsed_html'")

    if not parsed_html:
        uname = user if isinstance(user, str) else user['user']
        url = URL.format(uname=uname)
        parsed_html = make_request(url)

    if parsed_html.find_all("div", attrs={"class": "row login-denied"}):
        return True
    return False


def get_media(user, n=-1, since=None):
    if since:
        raise NotImplementedError()

    uname = user if isinstance(user, str) else user['user']
    url = URL.format(uname=uname)
    try:
        if n > 0 and n <= _PICBEAR_DEFAULT_PAGELOAD:
            dt = datetime.now()
            parsed_html = make_request(url)
        else:
            dt = datetime.now()
            parsed_html = make_scrolling_request(url)
    except Exception as e:  # :(
        if isinstance(e, urlliberror.HTTPError):
            raise HTTPRetreivalError(e.code) from e
        raise HTTPRetreivalError from e

    if is_private_account(parsed_html=parsed_html):
        raise PrivateAccountError()

    return (dt, *_extract_media_from_picbear(parsed_html, n))


def get_images(user, n=-1, since=None):
    rtn = get_media(user, -1, since)
    (dt, images, videos) = rtn                   # Bit of a hack here with
    images = images if n < 0 else images[:n]     # the n value... :(
    return (dt, images)


def get_videos(user, n=-1, since=None):
    rtn = get_media(user, -1, since)
    (dt, images, videos) = rtn                   # Bit of a hack here with
    videos = videos if n < 0 else videos[:n]     # the n value... :(
    return (dt, videos)


def get_metadata(picbear_url):
    logging.debug('get_metadata({}): IN'.format(picbear_url))
    parsed_html = make_request(picbear_url)
    if not parsed_html:
        raise UnexpectedResult()
    poll_dt = datetime.now()
    share_dt = datetime.strptime(
        _extract_datetimestr_from_picbear(parsed_html), PICBEAR_DATE_FORMAT
    )
    (like_count, likes) = _extract_likescomments_from_picbear(
        parsed_html, "likes"
    )
    (comment_count, comments) = _extract_likescomments_from_picbear(
        parsed_html, "comments"
    )
    caption = _extract_caption_from_picbear(parsed_html)
    return (
        poll_dt, share_dt, caption, like_count, comment_count, likes, comments
    )
