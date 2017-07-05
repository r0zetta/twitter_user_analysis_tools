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

    heatmap = []
    tweet_count = 0

    heatmap = [[0 for j in range(24)] for i in range(7)]

    for status in Cursor(auth_api.user_timeline, id=target).items():
        tweet_time = status.created_at + offset
        weekday = tweet_time.weekday()
        hour = tweet_time.hour
        tweet_count = tweet_count + 1
        heatmap[weekday][hour] = heatmap[weekday][hour] + 1
        sys.stdout.write("#")
        sys.stdout.flush()

    print "All done. Processed " + str(tweet_count) + " tweets."
    print
    filename = target.encode('utf-8') + "-heatmap.csv"
    print "Writing file: " + filename
    handle = open(filename, 'w')
    handle.write("Hour, 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23\n")
    handle.write("Mon, " + ','.join(map(str, heatmap[0])) + "\n")
    handle.write("Tue, " + ','.join(map(str, heatmap[1])) + "\n")
    handle.write("Wed, " + ','.join(map(str, heatmap[2])) + "\n")
    handle.write("Thu, " + ','.join(map(str, heatmap[3])) + "\n")
    handle.write("Fri, " + ','.join(map(str, heatmap[4])) + "\n")
    handle.write("Sat, " + ','.join(map(str, heatmap[5])) + "\n")
    handle.write("Sun, " + ','.join(map(str, heatmap[6])) + "\n")
    handle.close()




