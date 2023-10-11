import re

REGEX_TWITTER = re.compile('^(http|https):\/\/(?:www\.){0,1}(twitter|x)\.com.*')

def is_twitter_link(link):
    return re.match(REGEX_TWITTER, link) is not None

def replace_twitter_link(s: str) -> str:
    return re.sub(r'(?<!vx)(twitter|x\b)', 'vxtwitter', s)