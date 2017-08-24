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

count = 1
data = {}
target = "@r0zetta"
output_dir = "captures/"

def increment_counter(label, name):
    global data
    if label not in data:
        data[label] = {}
    if name not in data[label]:
        data[label][name] = 0
    data[label][name] += 1

def output_data():
    output_string = ""
    for label, stuff in sorted(data.iteritems()):
        output_string += u"\n" + label.encode('utf-8') + u":\n\n"
        for item, count in sorted(stuff.iteritems()):
            output_string += unicode(count) + u": " + unicode(item) + u"\n"
    return output_string

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
        created_second = "%02d" % status.created_at.second
        created_minute = "%02d" % status.created_at.minute
        created_hour = "%02d" % status.created_at.hour
        created_day = status.created_at.day
        created_month = status.created_at.month
        created_year = status.created_at.year
        date_string = str(created_year) + "/" + str(created_month) + "/" + str(created_day) + " " + str(created_hour) + ":" + str(created_minute) + ":" + str(created_second)
        text = status.text
        text = text.replace('\n', ' ').replace('\r', '')
        entry = date_string + " | " + status.text + "\n"
        tweet_texts.append(entry)

        if hasattr(status, 'in_reply_to_screen_name'):
            increment_counter("replied_to", status.in_reply_to_screen_name)

        if hasattr(status, 'lang'):
            increment_counter("languages", status.lang)

        retweeted = False
        if hasattr(status, 'retweeted_status'):
            orig_tweet = status.retweeted_status
            if hasattr(orig_tweet, 'user'):
                if orig_tweet.user is not None:
                    if hasattr(orig_tweet.user, "screen_name"):
                        if orig_tweet.user.screen_name is not None:
                            retweeted_user = orig_tweet.user.screen_name
                            increment_counter("retweeted", retweeted_user)
                            increment_counter("retweets", "count")

        if hasattr(status, 'quoted_status'):
            orig_tweet = status.quoted_status
            if 'user' in orig_tweet:
                if orig_tweet['user'] is not None:
                    if "screen_name" in orig_tweet['user']:
                        if orig_tweet['user']['screen_name'] is not None:
                            quoted_user = orig_tweet['user']['screen_name']
                            increment_counter("quoted", quoted_user)
                            increment_counter("quote_tweets", "count")
                            retweeted = True

        if hasattr(status, 'entities'):
            entities = status.entities
            if 'hashtags' in entities:
                for item in entities['hashtags']:
                    if item is not None:
                        tag = item['text']
                        if tag is not None:
                            if retweeted is True:
                                increment_counter("retweeted_hashtags", tag.lower())
                            else:
                                increment_counter("hashtags", tag.lower())
            if 'urls' in entities:
                for item in entities['urls']:
                    if item is not None:
                        url = item['expanded_url']
                        if url is not None:
                            if retweeted is True:
                                increment_counter("retweeted_urls", url)
                            else:
                                increment_counter("urls", url)
            if 'user_mentions' in entities:
                for item in entities['user_mentions']:
                    if item is not None:
                        mention = item['screen_name']
                        if mention is not None:
                            if retweeted is True:
                                increment_counter("retweeted_mentions", mention)
                            else:
                                increment_counter("mentions", mention)

# get user agents
        increment_counter("sources", status.source)

        sys.stdout.write("#")
        sys.stdout.flush()

    print
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
    handle = io.open(filename, 'w', encoding='utf-8')
    handle.write(u"User name: " + name.encode('utf-8') + u"\n")
    handle.write(u"Screen name: @" + screen_name.encode('utf-8') + u"\n")
    handle.write(u"User id: " + unicode(user_id) + u"\n")
    handle.write(u"Tweets: " + unicode(tweets) + u"\n")
    handle.write(u"Likes: " + unicode(likes) + u"\n")
    handle.write(u"Lists: " + unicode(lists) + u"\n")
    handle.write(u"Following: " + unicode(following) + u"\n")
    handle.write(u"Followers: " + unicode(followers) + u"\n")
    handle.write(u"Created: " + unicode(creation_date) + u"\n")
    data_string = output_data()
    handle.write(data_string)
    handle.close()


