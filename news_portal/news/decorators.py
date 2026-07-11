from django.contrib.auth.decorators import user_passes_test


def is_editor(user):
    return user.is_authenticated and getattr(user, "role", None) == "editor"


def editor_required(view_func):
    return user_passes_test(is_editor, login_url="/login/")(view_func)


def is_publisher(user):
    return user.is_authenticated and getattr(user, "role", None) == "publisher"


def publisher_required(view_func):
    return user_passes_test(is_publisher, login_url="/login/")(view_func)
