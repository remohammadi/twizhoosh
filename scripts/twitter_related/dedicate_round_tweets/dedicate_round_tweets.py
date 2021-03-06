import random
import re

from twython.exceptions import TwythonError

import settings
from core.scripts.twitter_related import base
from core.utils.logging import log


def cons_numbers(x):
    if len(x) < 4:
        return False

    inc_or_dec = 1 if x[1] > x[0] else -1

    for i in range(len(x) - 1):
        if int(x[i + 1]) - int(x[i]) != inc_or_dec:
            return False
    return True


def is_round(num):
    regex_patterns = [
        r'^[0-9]+000$',  # Numbers that end with 000
        r'^([0-9])\1+$',  # Numbers that are all equal
    ]

    function_patterns = [
        cons_numbers,  # Consecutive numbers, like 2345 or 8765
    ]

    if len(str(num)) < 3:
        return
    for regex in regex_patterns:
        if re.match(regex, str(num)):
            return True
    for f in function_patterns:
        if f(str(num)):
            return True
    return False


class DedicateRoundTweets(base.BaseOnSelfStatusUpdate):
    def get_all_friends(self):
        friends = []
        cursor = -1

        while cursor != 0:
            data = self.twitter.twitter.get_friends_list(screen_name=settings.TWIZHOOSH_USERNAME, count=200,
                                                         skip_status=1, include_user_entities="false", cursor=cursor)
            friends += data['users']
            cursor = data['next_cursor']

        return friends


    def dedicate_to(self):
        if not settings.DEBUG:
            # Correct way is to retrieve id's then show_user but doesn't work on heroku
            friends = self.get_all_friends()
            dedicated_to = random.choice(friends)['screen_name']
        else:
            dedicated_to = 'tester'
        log("Dedicate tweet to: " + dedicated_to)
        return dedicated_to


    def on_self_status_update(self, data):
        tweets = data['user']['statuses_count']
        log("Number of tweets: " + str(tweets))

        if is_round(tweets + 1):
            log("Next tweet is round")
            try:
                status = 'توییت {0} تقدیم به {1}.'.format(str(tweets + 1), '@' + self.dedicate_to())
            except TwythonError as e:
                log("Twython error: " + str(e))
                log("Last call headers:\n + " + str(self.twitter.twitter._last_call))
                status = 'توییت {0} رو هم تقدیم نمی‌کنیم...'.format(str(tweets + 1))
            self.twitter.tweet(status=status)