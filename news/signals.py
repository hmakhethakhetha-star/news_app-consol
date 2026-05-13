from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from .twitter_utils import post_tweet

@receiver(post_save, sender=Article)
def auto_tweet_on_publish(sender, instance, created, **kwargs):
    """
    Automatically tweet when an article is published.
    """
    # Only tweet when status changes to 'published'
    if instance.status == "published":
        tweet_text = f"📰 New article published: {instance.title}\nRead it now on NewsApp!"
        post_tweet(tweet_text)
