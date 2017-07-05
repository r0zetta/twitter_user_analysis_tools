from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from tweepy import TweepError
from datetime import datetime, date, time, timedelta
from inspect import getmembers
from twitter_authentication_keys import get_account_credentials
import pprint
import random
import time
import sys
import re
import os
import io

target_name = "@r0zetta"

if __name__ == '__main__':
    consumer_key, consumer_secret, access_token, access_token_secret = get_account_credentials()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth)

    count = 0
    query = '#generalelection'
    if (len(sys.argv) > 1):
            query = str(sys.argv[1])
    print "Signing in as: "+auth_api.me().name
    print "Querying: " + query

    retweet_count = 0
    replied_count = 0
    for item in Cursor(auth_api.search, q=query).items(1000):
        count += 1
        created_hour = item.created_at.hour
        created_day = item.created_at.day
        created_month = item.created_at.month
        created_year = item.created_at.year
        date_string = str(created_year) + "/" + str(created_month) + "/" + str(created_day) + " " + str(created_hour) + ":00"
        poster = item.user.screen_name.encode('utf-8')
        retweet_count = item.retweet_count
        is_retweet = "0"
        if "RT" in item.text[:4]:
            is_retweet = "1"
            retweet_count += 1
        replied_to = "None"
        if item.in_reply_to_screen_name is not None:
            replied_to = item.in_reply_to_screen_name.encode('utf-8')
            replied_count += 1
        print str(count) + " | " + date_string + " | " + poster + " | " + str(retweet_count) + " | " + is_retweet + " | " + replied_to

    retweet_percent = float(retweet_count)/float(count) * 100
    replied_percent = float(replied_count)/float(count) * 100
    print "Retweet count:" + str(retweet_count) + " percent: " + str(retweet_percent)
    print "Replied count:" + str(replied_count) + " percent: " + str(replied_percent)
