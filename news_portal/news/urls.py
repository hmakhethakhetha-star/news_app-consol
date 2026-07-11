from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Editor
    # -----------------------------
    path("editor/dashboard/", views.editor_dashboard, name="editor_dashboard"),
    path("editor/review/", views.editor_review_list, name="editor_review_list"),
    path("editor/review/<int:article_id>/", views.editor_review_detail, name="editor_review_detail"),
    path("editor/approve/<int:article_id>/", views.approve_article, name="approve_article"),
    path("editor/reject/<int:article_id>/", views.reject_article_editor, name="reject_article_editor"),

    # ✅ Publisher management (for editors)
    path("editor/publishers/", views.publisher_list, name="publisher_list"),
    path("editor/publishers/create/", views.publisher_create, name="publisher_create"),
    path("editor/publishers/<int:publisher_id>/edit/", views.publisher_edit, name="publisher_edit"),

    # ✅ Editor article management
    path("editor/article/<int:article_id>/edit/", views.update_article, name="update_article"),
    path("editor/article/<int:article_id>/delete/", views.delete_article, name="delete_article"),

    # ✅ Editor newsletter management
    path("editor/newsletters/", views.editor_newsletter_list, name="editor_newsletter_list"),
    path("editor/newsletter/<int:newsletter_id>/edit/", views.edit_newsletter, name="editor_edit_newsletter"),
    path("editor/newsletter/<int:newsletter_id>/delete/", views.delete_newsletter, name="editor_delete_newsletter"),

    # -----------------------------
    # Reader
    # -----------------------------
    path("reader/dashboard/", views.reader_dashboard, name="reader_dashboard"),
    path("", views.article_list, name="article_list"),
    path("article/<int:article_id>/", views.article_detail, name="article_detail"),
    path("subscribe_article/<int:article_id>/", views.subscribe_article, name="subscribe_article"),
    path("unsubscribe_article/<int:article_id>/", views.unsubscribe_article, name="unsubscribe_article"),

    # ✅ Reader newsletters
    path("reader/newsletters/", views.reader_newsletters, name="reader_newsletters"),

    # -----------------------------
    # Journalist
    # -----------------------------
    path("journalist/dashboard/", views.journalist_dashboard, name="journalist_dashboard"),
    path("journalist/article/create/", views.journalist_article_form, name="journalist_article_create"),
    path("journalist/article/<int:article_id>/edit/", views.journalist_article_form, name="journalist_article_edit"),
    path("submit-article/<int:article_id>/", views.submit_article, name="submit_article"),
    path("journalist/article/<int:article_id>/delete/", views.delete_article, name="journalist_article_delete"),

    # ✅ Journalist newsletters
    path("journalist/newsletters/", views.journalist_newsletter_dashboard, name="journalist_newsletter_dashboard"),
    path("journalist/newsletter/create/", views.create_newsletter, name="create_newsletter"),
    path("journalist/newsletter/<int:newsletter_id>/edit/", views.edit_newsletter, name="journalist_edit_newsletter"),
    path("journalist/newsletter/<int:newsletter_id>/delete/", views.delete_newsletter, name="journalist_delete_newsletter"),

    # -----------------------------
    # Publisher
    # -----------------------------
    path("register/", views.register, name="register"),
    path("publisher/dashboard/", views.publisher_dashboard, name="publisher_dashboard"),
    path("publisher/publish/<int:article_id>/", views.publish_article, name="publish_article"),
    path("publisher/reject/<int:article_id>/", views.reject_article_publisher, name="reject_article_publisher"),
    
    # -----------------------------
    # Subscriptions 
    # -----------------------------
    path("subscribe/publisher/<int:publisher_id>/", views.subscribe_publisher, name="subscribe_publisher"),
    path("unsubscribe/publisher/<int:publisher_id>/", views.unsubscribe_publisher, name="unsubscribe_publisher"),
    path("subscribe/journalist/<int:journalist_id>/", views.subscribe_journalist, name="subscribe_journalist"),
    path("unsubscribe/journalist/<int:journalist_id>/", views.unsubscribe_journalist, name="unsubscribe_journalist"),
]
