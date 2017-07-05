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

if __name__ == '__main__':
    consumer_key, consumer_secret, access_token, access_token_secret = get_account_credentials()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth)
    print "Signing in as: "+auth_api.me().name

    for status in Cursor(auth_api.user_timeline, id="@r0zetta").items():
        if(re.search("Android", status.source)):
            source = "Android"
        elif(re.search("iPhone", status.source)):
            source = "iPhone"
        else:
            source = status.source

        print source
