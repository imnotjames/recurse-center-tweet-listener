FROM python:3.8
LABEL description="A Twitter Stream Listener that Indexes to ElasticSearch"

ENV TWITTER_CONSUMER_KEY=""
ENV TWITTER_CONSUMER_KEY_SECRET=""
ENV TWITTER_ACCESS_TOKEN=""
ENV TWITTER_ACCESS_TOKEN_SECRET=""

ENV TWITTER_TERMS=""

ENV ELASTICSEARCH_HOSTS=""
ENV ELASTICSEARCH_INDEX="twitter"
ENV ELASTICSEARCH_DOCTYPE="tweet"

WORKDIR /app

ADD recurse_center_tweet_listener/ ./recurse_center_tweet_listener/
ADD requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "python", "-m", "recurse_center_tweet_listener" ]
