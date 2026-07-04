from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsStudent(BasePermission):
    """Allow access only to student users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'
