from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        USER=request.user
        
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(USER and USER.is_staff)     