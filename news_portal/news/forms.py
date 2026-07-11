from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Article, Publisher
from .models import Newsletter

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    User registration form with role selection.
    Publisher role is excluded because publishers are created by editors.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Remove publisher from role choices
        if 'role' in self.fields:
            self.fields['role'].choices = [
                choice for choice in self.fields['role'].choices
                if choice[0] != 'publisher'
            ]


class CustomAuthenticationForm(AuthenticationForm):
    """
    Login form for users.
    """
    class Meta:
        model = User
        fields = ("username", "password")


class PublisherForm(forms.ModelForm):
    manager_username = forms.CharField(max_length=150)
    manager_email = forms.EmailField()
    manager_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,  # ✅ allow blank when editing
        help_text="Leave blank to keep the current password."
    )

    class Meta:
        model = Publisher
        fields = ["name", "description"]

    def save(self, commit=True):
        publisher = super().save(commit=False)

        if publisher.manager:
            manager = publisher.manager
            manager.username = self.cleaned_data["manager_username"]
            manager.email = self.cleaned_data["manager_email"]
            if self.cleaned_data["manager_password"]:  # ✅ only update if provided
                manager.set_password(self.cleaned_data["manager_password"])
            manager.save()
        else:
            manager = User.objects.create_user(
                username=self.cleaned_data["manager_username"],
                email=self.cleaned_data["manager_email"],
                password=self.cleaned_data["manager_password"],
                role="publisher",
            )
            publisher.manager = manager

        if commit:
            publisher.save()
        return publisher


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["title", "content", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter newsletter title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Write your newsletter content here..."}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.role == "journalist":
            self.fields["status"].choices = [
                ("draft", "Draft"),
                ("submitted", "Submitted"),
            ]
        elif user and user.role == "editor":
            self.fields["status"].choices = [
                ("published", "Published"),
                ("rejected", "Rejected"),
            ]
