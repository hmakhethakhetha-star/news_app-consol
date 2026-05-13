from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Article, Publisher, User
from .serializers import ArticleSerializer


@api_view(["GET"])
def articles_by_publisher(request, publisher_id):
    """
    Return all approved articles for a given publisher.
    """
    publisher = get_object_or_404(Publisher, id=publisher_id)

    articles = Article.objects.filter(
        publisher=publisher,
        approved_by_editor=True,
        status="published"   # ✅ ensure only published articles are returned
    )

    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def articles_by_journalist(request, journalist_id):
    """
    Return all approved articles for a given journalist.
    """
    journalist = get_object_or_404(User, id=journalist_id)

    if journalist.role != "journalist":
        return Response(
            {"error": "User is not a journalist"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    articles = Article.objects.filter(
        author=journalist,
        approved_by_editor=True,
        status="published"   # ✅ only published articles
    )
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def subscribed_articles(request, user_id):
    """
    Return all approved articles from publishers and journalists
    that the specified reader is subscribed to.
    """
    reader = get_object_or_404(User, id=user_id)

    if reader.role != "reader":
        return Response(
            {"error": "User is not a reader"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    publisher_subs = reader.subscribed_publishers.all()   # ✅ now points to Publisher model
    journalist_subs = reader.subscribed_journalists.all()

    articles = (
        Article.objects
        .filter(approved_by_editor=True, status="published")
        .filter(
            Q(publisher__in=publisher_subs) |
            Q(author__in=journalist_subs)
        )
        .distinct()
    )

    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
