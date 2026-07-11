from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Newsletter, User, Article, Publisher, Journalist, Subscription

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ArticleForm
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import ArticleSerializer, PublisherSerializer, UserSerializer
from .permissions import IsJournalist, IsPublisher, IsOwnerOrReadOnly

from .decorators import editor_required, publisher_required
from .forms import PublisherForm, NewsletterForm


# -----------------------------
# Role-based Login
# -----------------------------
class RoleBasedLoginView(LoginView):
    """
    Custom login view that redirects users to their role-specific dashboard
    after successful authentication.

    Roles:
        - Editor → /editor/dashboard/
        - Journalist → /journalist/dashboard/
        - Reader → /reader/dashboard/
        - Publisher → /publisher/dashboard/
    """
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.role == "editor":
            return '/editor/dashboard/'
        elif user.role == "journalist":
            return '/journalist/dashboard/'
        elif user.role == "reader":
            return '/reader/dashboard/'
        elif user.role == "publisher":
            return '/publisher/dashboard/'
        return '/'


# -----------------------------
# Registration
# -----------------------------
def register(request):
    """
    Handle user registration.

    - Creates a new user account.
    - If the role is 'publisher', also creates a Publisher record linked
      to the user via the `manager` field.
    - If the role is 'journalist', also creates a Journalist record linked
      to the user via the `user` field.
    - Redirects to login page after successful registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user.role == "publisher":
                Publisher.objects.create(
                    manager=user,
                    name=f"{user.username}'s Publisher",
                    description="New publisher account"
                )

            elif user.role == "journalist":
                Journalist.objects.create(
                    user=user,
                    bio="New journalist account"
                )

            messages.success(request, "Account created successfully.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# -----------------------------
# Editor Views
# -----------------------------
@login_required
@editor_required
def editor_dashboard(request):
    """
    Editor dashboard view.

    - Displays all articles with status 'submitted'.
    - Shows all publishers for assignment purposes.
    """
    articles = Article.objects.filter(status="submitted")
    publishers = Publisher.objects.all()

    context = {
        "articles": articles,
        "publishers": publishers,
    }
    return render(request, "news/editor_dashboard.html", context)


@login_required
@editor_required
def editor_review_list(request):
    """
    List of articles awaiting editor approval.

    - Filters articles with status 'submitted'.
    - Used by editors to see pending review items.
    """
    articles = Article.objects.filter(status="submitted")
    return render(request, "news/editor_review_list.html", {"articles": articles})


@login_required
@editor_required
def editor_review_detail(request, article_id):
    """
    Detailed view of a submitted article for editors.

    - Displays article content.
    - Provides list of publishers for assignment if approved.
    """
    article = get_object_or_404(Article, id=article_id)
    publishers = Publisher.objects.all()
    return render(request, "news/editor_review_detail.html", {
        "article": article,
        "publishers": publishers,
    })


@login_required
@editor_required
def update_article(request, article_id):
    """
    Allow editors to update an article.

    - Editors can edit articles with status 'submitted' or 'editor_approved'.
    - Saves changes and redirects back to editor dashboard.
    """
    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "editor" and article.status in ["submitted", "editor_approved"]:
        if request.method == "POST":
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                messages.success(request, "Article updated by editor.")
                return redirect("editor_dashboard")
        else:
            form = ArticleForm(instance=article)
        return render(request, "news/article_edit.html", {"form": form, "article": article})

    else:
        messages.error(request, "You do not have permission to edit this article.")
        return redirect("article_list")


@login_required
@editor_required
def approve_article(request, article_id):
    """
    Approve an article at the editor stage.

    - Changes status to 'approved'.
    - Assigns article to a publisher if publisher_id is provided.
    - Redirects back to editor dashboard.
    """
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        article.status = "approved"

        publisher_id = request.POST.get("publisher_id")
        if publisher_id:
            article.publisher = Publisher.objects.get(id=publisher_id)

        article.save()
        messages.success(request, f"Article '{article.title}' approved and assigned to publisher.")
    return redirect("editor_dashboard")


@login_required
@editor_required
def reject_article_editor(request, article_id):
    """
    Reject an article at the editor stage.

    - Changes status to 'rejected'.
    - Redirects back to editor dashboard.
    """
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        article.status = "rejected"
        article.save()
        messages.warning(request, f"Article '{article.title}' rejected.")
    return redirect("editor_dashboard")


# -----------------------------
# Reader Views
# -----------------------------

@login_required
def reader_dashboard(request):
    """
    Reader dashboard view.

    - Displays all articles the reader is subscribed to.
    - Shows all published articles available for subscription.
    - Lists all published newsletters available for reading.
    - Lists all publishers and journalists available for subscription.
    """
    subscribed_articles = request.user.subscribed_articles.all()
    subscribed_publishers = request.user.subscribed_publishers.all()
    subscribed_journalists = request.user.subscribed_journalists.all()
    
    all_articles = Article.objects.filter(status="published")
    newsletters = Newsletter.objects.filter(status="published")
    publishers = Publisher.objects.all()
    journalists = Journalist.objects.all()
    print ("subscribed_journalist:", subscribed_journalists)
    print ("journalists:", journalists)

    return render(request, "news/reader_dashboard.html", {
        "subscribed_articles": subscribed_articles,
        "subscribed_publishers": subscribed_publishers,
        "subscribed_journalists": subscribed_journalists,
        "all_articles": all_articles,
        "newsletters": newsletters,
        "publishers": publishers,
        "journalists": journalists,
    })


# -----------------------------
# Reader Article Subscriptions
# -----------------------------
@login_required
def subscribe_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, status="published")
    request.user.subscribed_articles.add(article)
    return redirect("reader_dashboard")

@login_required
def unsubscribe_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    request.user.subscribed_articles.remove(article)
    return redirect("reader_dashboard")


# -----------------------------
# Reader Publisher Subscriptions
# -----------------------------
@login_required
def subscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    return redirect("reader_dashboard")


@login_required
def unsubscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.remove(publisher)
    return redirect("reader_dashboard")


# -----------------------------
# Reader Journalist Subscriptions
# -----------------------------
@login_required
def subscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(Journalist, id=journalist_id)
    request.user.subscribed_journalists.add(journalist.user)
    return redirect("reader_dashboard")


@login_required
def unsubscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(Journalist, id=journalist_id)
    request.user.subscribed_journalists.remove(journalist.user)
    return redirect("reader_dashboard")


# -----------------------------
# Reader Article Views
# -----------------------------
def article_list(request):
    articles = Article.objects.filter(status="published")
    return render(request, "news/article_list.html", {"articles": articles})


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id, )
    return render(request, "news/article_detail.html", {"article": article})

# -----------------------------
# Journalist Views
# -----------------------------
@login_required
def journalist_dashboard(request):
    """
    Journalist dashboard view.

    - Displays all articles authored by the current journalist.
    - Includes both draft and submitted articles.
    """
    articles = Article.objects.filter(author=request.user)
    return render(request, "news/journalist_dashboard.html", {"articles": articles})


@login_required
def journalist_article_form(request, article_id=None):
    """
    Create or edit an article as a journalist.

    - If article_id is provided, loads the existing article for editing.
    - Otherwise, creates a new article.
    - Saves the article with the current user as author.
    - Redirects back to journalist dashboard after save.
    """
    if article_id:
        article = Article.objects.get(pk=article_id)
        form = ArticleForm(request.POST or None, instance=article)
    else:
        form = ArticleForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        return redirect('journalist_dashboard')

    return render(request, "news/journalist_article_form.html", {"form": form})


@login_required
def submit_article(request, article_id):
    """
    Submit an article for editor review.

    - Changes status from 'draft' to 'submitted'.
    - Redirects back to journalist dashboard.
    """
    article = Article.objects.get(id=article_id)
    article.status = "submitted"
    article.save()
    return redirect("journalist_dashboard")


@login_required
def delete_article(request, article_id):
    """
    Delete an article with role-based restrictions.

    - Journalists can delete their own articles if status is 'draft' or 'submitted'.
    - Editors can delete any article if status is 'submitted' or 'editor_approved'.
    - Redirects to the appropriate dashboard after deletion.
    - Shows error message if user lacks permission.
    """
    article = get_object_or_404(Article, id=article_id)

    if request.user.role == "journalist" and article.author == request.user and article.status in ["draft", "submitted"]:
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect("journalist_dashboard")

    elif request.user.role == "editor" and article.status in ["submitted", "editor_approved"]:
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect("editor_dashboard")

    else:
        messages.error(request, "You do not have permission to delete this article.")
        return redirect("article_list")

# -----------------------------
# Newsletter
# -----------------------------

# -----------------------------
# Journalist Newsletters
# -----------------------------
@login_required
def journalist_newsletter_dashboard(request):
    """
    Journalist dashboard for newsletters.

    - Displays all newsletters authored by the current journalist.
    - Orders newsletters by most recently updated.
    """
    newsletters = Newsletter.objects.filter(author=request.user).order_by("-updated_at")
    return render(request, "news/journalist_newsletters.html", {"newsletters": newsletters})


@login_required
def create_newsletter(request):
    """
    Create a new newsletter as a journalist.

    - Only journalists can create newsletters.
    - Saves the newsletter with the current user as author.
    - Redirects back to journalist newsletter dashboard after creation.
    """
    if request.user.role != "journalist":
        messages.error(request, "Only journalists can create newsletters.")
        return redirect("article_list")

    if request.method == "POST":
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            messages.success(request, "Newsletter created.")
            return redirect("journalist_newsletter_dashboard")
    else:
        form = NewsletterForm(user=request.user)
    return render(request, "news/newsletter_form.html", {"form": form})


@login_required
def edit_newsletter(request, newsletter_id):
    """
    Edit an existing newsletter.

    - Journalists can edit their own newsletters.
    - Editors can edit any newsletter.
    - Redirects to the appropriate dashboard after update.
    """
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user.role == "journalist" and newsletter.author == request.user:
        pass
    elif request.user.role == "editor":
        pass
    else:
        messages.error(request, "You do not have permission to edit this newsletter.")
        return redirect("article_list")

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated.")
            if request.user.role == "journalist":
                return redirect("journalist_newsletter_dashboard")
            else:
                return redirect("editor_newsletter_list")
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(request, "news/newsletter_form.html", {"form": form, "newsletter": newsletter})


@login_required
def delete_newsletter(request, newsletter_id):
    """
    Delete a newsletter with role-based restrictions.

    - Journalists can delete their own newsletters if status is 'draft' or 'submitted'.
    - Editors can delete any newsletter regardless of status.
    - Redirects to the appropriate dashboard after deletion.
    - Shows error message if user lacks permission.
    """
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.user.role == "journalist" and newsletter.author == request.user:
        if newsletter.status in ["draft", "submitted"]:
            newsletter.delete()
            messages.success(request, "Newsletter deleted.")
        else:
            messages.error(request, "You can only delete draft or submitted newsletters.")
        return redirect("journalist_newsletter_dashboard")

    elif request.user.role == "editor":
        newsletter.delete()
        messages.success(request, "Newsletter deleted.")
        return redirect("editor_newsletter_list")

    else:
        messages.error(request, "You do not have permission to delete this newsletter.")
        return redirect("article_list")


# -----------------------------
# Editor Newsletters
# -----------------------------
@login_required
def editor_newsletter_list(request):
    """
    Editor view of all newsletters.

    - Only editors can access this view.
    - Displays all newsletters ordered by most recent update.
    - Editors can update or delete newsletters from this list.
    """
    if request.user.role != "editor":
        messages.error(request, "Only editors can view newsletters.")
        return redirect("article_list")

    newsletters = Newsletter.objects.all().order_by("-updated_at")
    return render(request, "news/editor_newsletters.html", {"newsletters": newsletters})


# -----------------------------
# Reader Newsletters
# -----------------------------
def reader_newsletters(request):
    """
    Public list of published newsletters.

    - Accessible without login.
    - Displays newsletters with status 'published'.
    - Readers can view but not edit or delete newsletters.
    """
    newsletters = Newsletter.objects.filter(status="published").order_by("-updated_at")
    return render(request, "news/reader_newsletters.html", {"newsletters": newsletters})

# -----------------------------
# Publisher Management (Editors)
# -----------------------------
@login_required
@editor_required
def publisher_list(request):
    """
    Editor view of all publishers.

    - Accessible only to editors.
    - Displays a list of all publisher accounts.
    - Used for managing publisher records.
    """
    publishers = Publisher.objects.all()
    return render(request, "news/publisher_list.html", {"publishers": publishers})


@login_required
@editor_required
def publisher_create(request):
    """
    Create a new publisher account.

    - Accessible only to editors.
    - Creates a Publisher record and associated manager user.
    - After creation, shows confirmation page with manager credentials.
    """
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            context = {
                "publisher": publisher,
                "username": form.cleaned_data["manager_username"],
                "password": form.cleaned_data["manager_password"],
            }
            return render(request, "news/publisher_confirmation.html", context)
    else:
        form = PublisherForm()
    return render(request, "news/publisher_form.html", {"form": form})


@login_required
@editor_required
def publisher_edit(request, publisher_id):
    """
    Edit an existing publisher account.

    - Accessible only to editors.
    - Allows updating publisher details and manager information.
    - Redirects back to publisher list after successful update.
    """
    publisher = get_object_or_404(Publisher, id=publisher_id)

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect("publisher_list")
    else:
        initial = {
            "manager_username": publisher.manager.username,
            "manager_email": publisher.manager.email,
        }
        form = PublisherForm(instance=publisher, initial=initial)

    return render(request, "news/publisher_form.html", {"form": form})


# -----------------------------
# Publisher Actions (Publish/Reject)
# -----------------------------
@login_required
@publisher_required
def publisher_dashboard(request):
    """
    Publisher dashboard view.

    - Accessible only to publishers.
    - Displays all articles assigned to the publisher with status 'approved'.
    - Publishers can then publish or reject these articles.
    """
    publisher = Publisher.objects.filter(manager=request.user).first()
    if not publisher:
        messages.error(request, "You are not assigned as a publisher.")
        return redirect("article_list")

    articles = Article.objects.filter(status="approved", publisher=publisher)
    return render(request, "news/publisher_dashboard.html", {"articles": articles})


@login_required
@publisher_required
def publish_article(request, article_id):
    """
    Publish an article as a publisher.

    - Accessible only to publishers.
    - Changes article status from 'approved' to 'published'.
    - Assigns the article to the current publisher.
    - Redirects back to publisher dashboard after publishing.
    """
    article = get_object_or_404(Article, id=article_id)
    publisher = Publisher.objects.filter(manager=request.user).first()
    if request.method == "POST" and publisher:
        article.status = "published"
        article.publisher = publisher
        article.save()
        messages.success(request, f"Article '{article.title}' published.")
    return redirect("publisher_dashboard")


@login_required
@publisher_required
def reject_article_publisher(request, article_id):
    """
    Reject an article at the publisher stage.

    - Accessible only to publishers.
    - Changes article status from 'approved' to 'rejected'.
    - Assigns the article to the current publisher.
    - Redirects back to publisher dashboard after rejection.
    """
    article = get_object_or_404(Article, id=article_id)
    publisher = Publisher.objects.filter(manager=request.user).first()
    if request.method == "POST" and publisher:
        article.status = "rejected"
        article.publisher = publisher
        article.save()
        messages.warning(request, f"Article '{article.title}' rejected.")
    return redirect("publisher_dashboard")

# -----------------------------
# RESTful API ViewSets
# -----------------------------
class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoints for published articles.

    - Provides CRUD operations for articles.
    - Journalists can create, update, or delete their own articles.
    - Read-only access is allowed for all users.
    - Only articles with status 'published' are exposed in the queryset.
    """
    queryset = Article.objects.filter(status="published")
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """
        Define permissions based on action.

        - Create, update, partial_update, destroy → Journalist + Owner permissions.
        - Read-only actions → Public access.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsJournalist(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """
        Save a new article with the current user as author.
        """
        serializer.save(author=self.request.user)


class PublisherArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoints for publishers to manage editor-approved articles.

    - Queryset includes articles with status 'editor_approved'.
    - Publishers can publish or reject articles via custom actions.
    """
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(status="editor_approved")

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """
        Publish an editor-approved article.

        - Changes status to 'published'.
        - Assigns the article to the current publisher.
        """
        article = self.get_object()
        publisher = Publisher.objects.filter(manager=request.user).first()
        if not publisher:
            return Response({"error": "You are not assigned as a publisher."},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = "published"
        article.publisher = publisher
        article.save()
        return Response({"status": f"Article '{article.title}' published"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Reject an editor-approved article.

        - Changes status to 'rejected'.
        - Assigns the article to the current publisher.
        """
        article = self.get_object()
        publisher = Publisher.objects.filter(manager=request.user).first()
        if not publisher:
            return Response({"error": "You are not assigned as a publisher."},
                            status=status.HTTP_403_FORBIDDEN)

        article.status = "rejected"
        article.publisher = publisher
        article.save()
        return Response({"status": f"Article '{article.title}' rejected"},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for user accounts.

    - Read-only access to user data.
    - Requires authentication.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["GET"])
def api_subscribed_articles(request, reader_id):
    """
    Retrieve all articles subscribed to by a reader.

    - Includes articles from subscribed publishers and journalists.
    - Only published articles are returned.
    - Returns serialized list of articles.
    """
    reader = User.objects.get(id=reader_id, role="reader")

    publisher_articles = Article.objects.filter(
        publisher__in=reader.subscribed_publishers.all(),
        status="published",
    )
    journalist_articles = Article.objects.filter(
        author__in=reader.subscribed_journalists.all(),
        status="published",
    )

    articles = publisher_articles.union(journalist_articles)
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


class EditorArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoints for editors to review and manage articles.

    - Queryset includes articles with status 'submitted'.
    - Editors can approve or reject articles via custom actions.
    """
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(status="submitted")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """
        Approve a submitted article.

        - Changes status to 'approved'.
        - Makes the article available for publisher review.
        """
        article = self.get_object()
        article.status = "approved"
        article.save()
        return Response({"status": "Article approved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Reject a submitted article.

        - Changes status to 'rejected'.
        - Article is removed from the editor review queue.
        """
        article = self.get_object()
        article.status = "rejected"
        article.save()
        return Response({"status": "Article rejected"}, status=status.HTTP_200_OK)
