from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Добавлять/удалять/редактировать можно только админам."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.is_staff:
            return True


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Добавлять/удалять/редактировать можно только авторам."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        if obj.author == request.user:
            return True


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешает изменение только владельцу или админу."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user == obj.user or request.user.is_staff:
            return True
