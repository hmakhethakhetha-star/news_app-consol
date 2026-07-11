from django.urls import path

from . import api_views

urlpatterns = [
    path(
        "publisher/<int:publisher_id>/articles/",
        api_views.articles_by_publisher,
        name="api_articles_by_publisher",
    ),
    path(
        "journalist/<int:journalist_id>/articles/",
        api_views.articles_by_journalist,
        name="api_articles_by_journalist",
    ),
    path(
        "reader/<int:user_id>/subscriptions/articles/",
        api_views.subscribed_articles,
        name="api_subscribed_articles",
    ),
]
