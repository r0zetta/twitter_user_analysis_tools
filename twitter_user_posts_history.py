from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from twitter_authentication_keys import get_account_credentials
import pprint
import random
import time
import hashlib
import base64
import sys
import re

count = 1
offset = timedelta(hours = 3)
target = "@r0zetta"


if __name__ == '__main__':
    consumer_key, consumer_secret, access_token, access_token_secret = get_account_credentials()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth)

    if (len(sys.argv) > 1):
            target = str(sys.argv[1])

    print "Signing in as: "+auth_api.me().name
    print "Target: " + target.encode('utf-8')

    tweet_count = 0

    tweets = []
    for status in Cursor(auth_api.user_timeline, id=target).items():
        tweet_count = tweet_count + 1
        created_hour = status.created_at.hour
        created_day = status.created_at.day
        created_month = status.created_at.month
        created_year = status.created_at.year
        date_string = str(created_year) + "/" + str(created_month) + "/" + str(created_day) + " " + str(created_hour) + ":00"
        text = status.text
        text = text.replace('\n', ' ').replace('\r', '')
        entry = date_string + " | " + status.text + "\n"
        tweets.append(entry)
        sys.stdout.write("#")
        sys.stdout.flush()



    print "All done. Processed " + str(tweet_count) + " tweets."
    print
    filename = target.encode('utf-8') + "-tweets.txt"
    print "Writing file: " + filename
    handle = open(filename, 'w')
    for text in tweets:
        handle.write(text.encode('utf-8'))
    handle.close()




