from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Article, Publisher

User = get_user_model()


class SubscriptionAPITests(TestCase):
    def setUp(self):
        # Reset database
        Article.objects.all().delete()
        Publisher.objects.all().delete()
        User.objects.all().delete()

        self.client = APIClient()

        # Reader
        self.reader = User.objects.create_user(
            username="reader1", password="pass123", role="reader"
        )

        # Journalists
        self.journalist1 = User.objects.create_user(
            username="journalist1", password="pass123", role="journalist"
        )
        self.journalist2 = User.objects.create_user(
            username="journalist2", password="pass123", role="journalist"
        )

        # Publishers
        self.publisher_user1 = User.objects.create_user(
            username="publisher_user1", password="pass123", role="publisher"
        )
        self.publisher_user2 = User.objects.create_user(
            username="publisher_user2", password="pass123", role="publisher"
        )
        self.publisher1 = Publisher.objects.create(
            name="Publisher A", description="Desc A", manager=self.publisher_user1
        )
        self.publisher2 = Publisher.objects.create(
            name="Publisher B", description="Desc B", manager=self.publisher_user2
        )

        # Articles
        Article.objects.create(
            title="Article from Publisher A",
            content="Content A",
            publisher=self.publisher1,
            author=self.journalist1,
            status="published",
        )
        Article.objects.create(
            title="Article from Publisher B",
            content="Content B",
            publisher=self.publisher2,
            author=self.journalist2,
            status="published",
        )
        Article.objects.create(
            title="Unapproved Article",
            content="Not approved",
            publisher=self.publisher1,
            author=self.journalist1,
            status="draft",  # not visible to readers
        )

        # Reader subscriptions
        self.reader.subscribed_publishers.add(self.publisher1)
        self.reader.subscribed_journalists.add(self.journalist2)

        # Authenticate as reader
        self.client.force_authenticate(user=self.reader)

    def test_reader_gets_articles_from_subscribed_publishers(self):
        url = reverse("api_subscribed_articles", args=[self.reader.id])
        response = self.client.get(url)
        titles = [article["title"] for article in response.data]
        self.assertIn("Article from Publisher A", titles)

    def test_reader_gets_articles_from_subscribed_journalists(self):
        url = reverse("api_subscribed_articles", args=[self.reader.id])
        response = self.client.get(url)
        titles = [article["title"] for article in response.data]
        self.assertIn("Article from Publisher B", titles)

    def test_reader_does_not_get_unapproved_articles(self):
        url = reverse("api_subscribed_articles", args=[self.reader.id])
        response = self.client.get(url)
        titles = [article["title"] for article in response.data]
        self.assertNotIn("Unapproved Article", titles)

    def test_reader_with_no_subscriptions_gets_empty_list(self):
        new_reader = User.objects.create_user(
            username="reader2", password="pass123", role="reader"
        )
        self.client.force_authenticate(user=new_reader)
        url = reverse("api_subscribed_articles", args=[new_reader.id])
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)
