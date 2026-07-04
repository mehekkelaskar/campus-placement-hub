import pytest
from unittest.mock import MagicMock

from apps.users.permissions import IsAdmin, IsStudent


class TestIsAdminPermission:
    def test_admin_user_allowed(self, admin_user):
        request = MagicMock()
        request.user = admin_user
        perm = IsAdmin()
        assert perm.has_permission(request, None) is True

    def test_student_user_denied(self, student_user):
        request = MagicMock()
        request.user = student_user
        perm = IsAdmin()
        assert perm.has_permission(request, None) is False

    def test_anonymous_user_denied(self):
        request = MagicMock()
        request.user = MagicMock()
        request.user.is_authenticated = False
        perm = IsAdmin()
        assert perm.has_permission(request, None) is False


class TestIsStudentPermission:
    def test_student_user_allowed(self, student_user):
        request = MagicMock()
        request.user = student_user
        perm = IsStudent()
        assert perm.has_permission(request, None) is True

    def test_admin_user_denied(self, admin_user):
        request = MagicMock()
        request.user = admin_user
        perm = IsStudent()
        assert perm.has_permission(request, None) is False

    def test_anonymous_user_denied(self):
        request = MagicMock()
        request.user = MagicMock()
        request.user.is_authenticated = False
        perm = IsStudent()
        assert perm.has_permission(request, None) is False
