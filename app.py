import os
import time
from twython import Twython
from abstracts import justone

CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']
TWEET_LENGTH = 140
TWEET_URL_LENGTH = 21

TWEET_EVERY_N_SECONDS = 60*10 # e.g. 60*10 = ten minutes between each tweet

def twitter_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def submit_tweet(message, handle=None):
    if not handle:
        handle = twitter_handle()
    handle.update_status(status=message)

def get_message(handle):
    message = '"' + justone(pred=lambda x: len(x) <= TWEET_LENGTH-2) + '"'
    assert len(message) <= TWEET_LENGTH-2
    return message

def main():
    handle = twitter_handle()
    while True:
        message = get_message(handle)
        print message
        submit_tweet(message, handle)
        time.sleep(TWEET_EVERY_N_SECONDS)

if __name__ == '__main__':
    main()
