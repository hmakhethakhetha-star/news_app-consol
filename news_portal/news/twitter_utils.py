import tweepy
from django.conf import settings


def get_twitter_client():
    """
    Returns a Tweepy Client configured for the v2 API.
    """
    return tweepy.Client(
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
    )


def post_tweet(message: str):
    """
    Posts a tweet using the v2 API.
    """
    client = get_twitter_client()
    try:
        response = client.create_tweet(text=message)
        print(f"Tweet posted! ID: {response.data['id']}")
        return response.data['id']
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")
        return None


