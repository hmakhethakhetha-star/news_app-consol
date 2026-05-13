"""
URL configuration for news_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from news.views import RoleBasedLoginView
from news import views
from django.contrib.auth.views import LogoutView

# 🔑 Add DRF imports
from rest_framework.routers import DefaultRouter
from news.views import ArticleViewSet, PublisherArticleViewSet, UserViewSet, EditorArticleViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Register API ViewSets
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename="article")
router.register(r'publishers', PublisherArticleViewSet, basename="publisher-articles")
router.register(r'users', UserViewSet, basename="user")
router.register(r'editor/articles', EditorArticleViewSet, basename="editor-articles")  

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),

    # Dashboards
    path("publisher/", views.publisher_dashboard, name="publisher_dashboard"),
    path("", include("news.urls")), 

    # -----------------------------
    # RESTful API routes
    # -----------------------------
    path("api/", include(router.urls)),

    # JWT Authentication endpoints
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Reader subscriptions
    path("api/readers/<int:reader_id>/subscriptions/", views.api_subscribed_articles, name="api_subscribed_articles"),
]
