from dotenv import load_dotenv
load_dotenv()

import logging
import os
import sys

from elasticsearch import Elasticsearch

from tweepy import OAuthHandler
from tweepy import Stream

from recurse_center_tweet_listener import ElasticsearchIndexingStreamListener, LoggingStreamListener

if __name__ == '__main__':
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger().setLevel(logging.DEBUG)

    twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    twitter_consumer_key_secret = os.environ['TWITTER_CONSUMER_KEY_SECRET']
    twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
    twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    twitter_terms = [t for t in os.environ.get('TWITTER_TERMS', '').split(',') if t]

    elasticsearch_hosts = [h for h in os.environ.get('ELASTICSEARCH_HOSTS', '').split(',') if h]
    elasticsearch_index = os.environ.get('ELASTICSEARCH_INDEX', 'twitter')
    elasticsearch_doctype = os.environ.get('ELASTICSEARCH_DOCTYPE', 'tweet')

    twitter_auth = OAuthHandler(twitter_consumer_key, twitter_consumer_key_secret)
    twitter_auth.set_access_token(twitter_access_token, twitter_access_token_secret)

    if len(twitter_terms) == 0:
        raise Exception("Must specify at least one twitter term")

    if len(elasticsearch_hosts) > 0:
        listener = ElasticsearchIndexingStreamListener(
            Elasticsearch(elasticsearch_hosts),
            elasticsearch_index,
            elasticsearch_doctype
        )
    else:
        listener = LoggingStreamListener()

    twitter_stream = Stream(twitter_auth, listener)

    twitter_stream.filter(track=twitter_terms, languages=os.environ.get('TWITTER_LANGUAGE', 'en').split(','))
