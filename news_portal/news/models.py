from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
        ('publisher', 'Publisher'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Reader-only fields
    subscribed_publishers = models.ManyToManyField(
        'Publisher',   # ✅ should point to Publisher, not User
        related_name='subscribed_readers',
        blank=True,
    )
    subscribed_journalists = models.ManyToManyField(
        'User',
        related_name='followers',
        blank=True,
    )

    # Journalist-only fields
    independent_articles = models.ManyToManyField(
        'Article',
        related_name='independent_authors',
        blank=True,
    )
    independent_newsletters = models.TextField(blank=True, null=True)

    def clean_role_fields(self):
        if self.role == 'journalist':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()
        if self.role == 'reader':
            self.independent_articles.clear()
            self.independent_newsletters = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clean_role_fields()
        super().save(update_fields=['independent_newsletters'])


class Publisher(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    # Manager is an editor user who oversees this publisher
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_publishers",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("editor_approved", "Editor Approved"),
        ("published", "Published"),
        ("rejected", "Rejected"),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="subscribed_articles",
        blank=True
    )

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)  # journalist/editor
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("editor_approved", "Editor Approved"),
            ("published", "Published"),
            ("rejected", "Rejected"),
        ],
        default="draft",
    )

    def __str__(self):
        return self.title


class Journalist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)


class Subscription(models.Model):
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("reader", "journalist", "publisher")
