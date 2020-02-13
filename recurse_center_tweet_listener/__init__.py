from dotenv import load_dotenv
load_dotenv()

import json
import logging
import time

from textblob import TextBlob

from tweepy.streaming import StreamListener


logger = logging.getLogger(__name__)


class LambdaStreamListener(StreamListener):
    def __init__(self, callable):
        self.callable = callable

    def on_data(self, data):
        tweet_json = json.loads(data)

        if 'text' not in tweet_json.keys():
            return True

        tweet_text_blob = TextBlob(tweet_json["text"])

        text_polarity = tweet_text_blob.sentiment.polarity
        subjectivity = tweet_text_blob.sentiment.subjectivity

        if text_polarity == 0:
            sentiment = "Neutral"
        elif text_polarity < 0:
            sentiment = "Negative"
        elif text_polarity > 0:
            sentiment = "Positive"
        else:
            sentiment = "UNKNOWN"

        logger.debug('TextBlob Analysis Sentiment: {}'.format(sentiment))

        body = {
            "tweet_id": tweet_json["id_str"],
            "tweet_timestamp_ms": tweet_json["timestamp_ms"],
            "tweet_date": tweet_json["created_at"],
            "is_quote_status": tweet_json["is_quote_status"],
            "in_reply_to_status_id": tweet_json["in_reply_to_status_id"],
            "in_reply_to_screen_name": tweet_json["in_reply_to_screen_name"],
            "favorite_count": tweet_json["favorite_count"],
            "author": tweet_json["user"]["screen_name"],
            "tweet_text": tweet_json["text"],
            "retweeted": tweet_json["retweeted"],
            "retweet_count": tweet_json["retweet_count"],
            "geo": tweet_json["geo"],
            "place": tweet_json["place"],
            "coordinates": tweet_json["coordinates"],
            "polarity": text_polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment,
            "ingested_timestamp_ms": time.time_ns() // 1000000
        }

        try:
            self.callable(body)
        except BaseException as err:
            logger.exception("Exception writing tweet to ES: {}".format(err))

        return True

    def on_error(self, status):
        logger.error("Fatal Error: {}".format(status))
        return False


class LoggingStreamListener(LambdaStreamListener):
    def __init__(self):
        super().__init__(lambda body: logger.info(body))


class ElasticsearchIndexingStreamListener(LambdaStreamListener):
    def __init__(self, client, index, doctype):
        super().__init__(lambda body: client.index(
            id=body['tweet_id'],
            index=index,
            doc_type=doctype,
            body=body
        ))
