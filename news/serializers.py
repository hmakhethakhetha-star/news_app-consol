from rest_framework import serializers
from .models import Article, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serialize basic publisher information.
    """
    class Meta:
        model = Publisher
        fields = ["id", "name", "description"]


class JournalistSerializer(serializers.ModelSerializer):
    """
    Serialize basic journalist information.
    """
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]
        read_only_fields = fields


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serialize articles with nested publisher and author info.
    """
    publisher = PublisherSerializer(read_only=True)
    author = JournalistSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "publisher",
            "author",
            "status",              # ✅ include status for clarity
            "created_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize user information including role (journalist/publisher/reader/editor).
    """
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        read_only_fields = ["id"]

