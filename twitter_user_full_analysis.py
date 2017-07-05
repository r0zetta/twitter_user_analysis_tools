from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from twitter_authentication_keys import get_account_credentials
import numpy as np
import os.path
import random
import time
import sys
import re
import os
import io

"""
response = unirest.post("https://osome-botometer.p.mashape.com/2/check_account",
  headers={
    "X-Mashape-Key": "dHKciNZ54Smsh8d51b7U7dpFSoaQp1dAWjwjsnmtFG3yrwcthq",
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  params=("{\"user\":{\"id\":\"1234567890\",\"screen_name\":\"IUNetSci\"},\"timeline\":[{\"id\":1234567890,\"text\":\"@Botometer is so cool!\",\"...\":\"...\"},\"...\"],\"mentions\":[{\"id\":9876543210,\"text\":\"@TruthyAtIndiana is also cool!\",\"...\":\"...\"},\"...\"]}")
)
"""

count = 1
target = "@r0zetta"
output_dir = "captures/"

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

    heatmap = []
    interarrivals = {}
    tweet_texts = []
    sources = {}

    heatmap = [[0 for j in range(24)] for i in range(7)]

    item = auth_api.get_user(target)
# Get year and month of account creation
    name = item.name
    screen_name = item.screen_name
    user_id = item.id_str
    tweets = str(item.statuses_count)
    likes = str(item.favourites_count)
    lists = str(item.listed_count)
    following = str(item.friends_count)
    followers = str(item.followers_count)
    created_month = item.created_at.month
    created_year = item.created_at.year
    creation_date = str(created_month) + "/" + str(created_year)
    #following_list = auth_api.friends_ids(target)
    #followers_list = auth_api.followers_ids(target)

    previous_tweet_time = None
    for status in Cursor(auth_api.user_timeline, id=target).items():
        tweet_count = tweet_count + 1

# create heatmap
        tweet_time = status.created_at
        weekday = tweet_time.weekday()
        hour = tweet_time.hour
        heatmap[weekday][hour] = heatmap[weekday][hour] + 1

# get interarrival map
        current_tweet_time = status.created_at
        if previous_tweet_time is not None:
            delta = previous_tweet_time - current_tweet_time
            delta_seconds = int(delta.total_seconds())
            if delta_seconds not in interarrivals:
                interarrivals[delta_seconds] = 1
            else:
                interarrivals[delta_seconds] += 1
        previous_tweet_time = current_tweet_time

# get all tweet texts
        created_minute = status.created_at.minute
        created_hour = status.created_at.hour
        created_day = status.created_at.day
        created_month = status.created_at.month
        created_year = status.created_at.year
        date_string = str(created_year) + "/" + str(created_month) + "/" + str(created_day) + " " + str(created_hour) + ":" + str(created_minute)
        text = status.text
        text = text.replace('\n', ' ').replace('\r', '')
        entry = date_string + " | " + status.text + "\n"
        tweet_texts.append(entry)

# get user agents
        source = status.source
        if source not in sources:
            sources[source] = 1
        else:
            sources[source] += 1

        sys.stdout.write("#")
        sys.stdout.flush()

    print "All done. Processed " + str(tweet_count) + " tweets."
    print

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = output_dir + target.encode('utf-8') + "-interarrivals.txt"
    print "Writing file: " + filename
    handle = open(filename, 'w')
    std = np.std(interarrivals.values())
    handle.write("Standard deviation: " + str(std) + "\n")
    for key in sorted(interarrivals.iterkeys()):
        outstring = str(key) + " | " + str(interarrivals[key]) + "\n"
        handle.write(outstring.encode('utf-8'))
    handle.close()

    filename = output_dir + target.encode('utf-8') + "-tweets.txt"
    print "Writing file: " + filename
    handle = open(filename, 'w')
    for text in tweet_texts:
        handle.write(text.encode('utf-8'))
    handle.close()

    filename = output_dir + target.encode('utf-8') + "-heatmap.csv"
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

    filename = output_dir + target.encode('utf-8') + "-details.txt"
    print "Writing file: " + filename
    handle = open(filename, 'w')
    handle.write("User name: " + name.encode('utf-8') + "\n")
    handle.write("Screen name: @" + screen_name.encode('utf-8') + "\n")
    handle.write("User id: " + user_id + "\n")
    handle.write("Tweets: " + tweets + "\n")
    handle.write("Likes: " + likes + "\n")
    handle.write("Lists: " + lists + "\n")
    handle.write("Following: " + following + "\n")
    handle.write("Followers: " + followers + "\n")
    handle.write("Created: " + creation_date + "\n")
    handle.write("Sources:\n")
    for source, count in sources.iteritems():
        handle.write(source + ": " + str(count) + "\n")
    handle.close()


