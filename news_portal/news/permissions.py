from rest_framework import permissions


def user_has_role(user, role_name):
    """
    Safely check if a user has a given role.
    Prevents AttributeError if 'role' is missing.
    """
    return getattr(user, "role", None) == role_name


class IsReader(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'reader'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and user_has_role(request.user, "reader")


class IsJournalist(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'journalist'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and user_has_role(request.user, "journalist")


class IsPublisher(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'publisher'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and user_has_role(request.user, "publisher")


class IsEditor(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'editor'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and user_has_role(request.user, "editor")


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: allow owners to edit, others read-only.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the author/owner
        return getattr(obj, "author", None) == request.user
