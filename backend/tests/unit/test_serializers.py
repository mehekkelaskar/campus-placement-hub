import pytest
from apps.users.serializers import RegisterSerializer, UserProfileSerializer, AdminStudentSerializer
from apps.companies.serializers import CompanyListSerializer, CompanyDetailSerializer, CompanyCreateUpdateSerializer, PlacementDriveSerializer
from apps.bookmarks.serializers import BookmarkSerializer


# ============================================================
# RegisterSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestRegisterSerializer:
    def test_valid_registration(self):
        data = {
            'email': 'new@test.com', 'username': 'newuser',
            'first_name': 'New', 'last_name': 'User',
            'password': 'StrongPass1!', 'password2': 'StrongPass1!',
            'branch': 'CSE', 'year': 4,
        }
        s = RegisterSerializer(data=data)
        assert s.is_valid(), s.errors
        user = s.save()
        assert user.email == 'new@test.com'
        assert user.role == 'student'
        assert user.check_password('StrongPass1!')

    def test_password_mismatch(self):
        data = {
            'email': 'p@t.com', 'username': 'puser',
            'first_name': 'P', 'last_name': 'U',
            'password': 'StrongPass1!', 'password2': 'DifferentPass1!',
            'branch': 'CSE', 'year': 4,
        }
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert 'password2' in s.errors

    def test_weak_password(self):
        data = {
            'email': 'w@t.com', 'username': 'wuser',
            'first_name': 'W', 'last_name': 'U',
            'password': '123', 'password2': '123',
            'branch': 'CSE', 'year': 4,
        }
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert 'password' in s.errors

    def test_missing_email(self):
        data = {
            'username': 'noemail', 'first_name': 'N', 'last_name': 'E',
            'password': 'StrongPass1!', 'password2': 'StrongPass1!',
        }
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert 'email' in s.errors

    def test_missing_required_fields(self):
        s = RegisterSerializer(data={})
        assert not s.is_valid()
        # Should have errors for required fields
        assert len(s.errors) > 0

    def test_duplicate_email(self, student_user):
        data = {
            'email': 'student_test@plc.com', 'username': 'dup',
            'first_name': 'D', 'last_name': 'U',
            'password': 'StrongPass1!', 'password2': 'StrongPass1!',
        }
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert 'email' in s.errors

    def test_password_not_in_output(self):
        data = {
            'email': 'sec@t.com', 'username': 'secuser',
            'first_name': 'S', 'last_name': 'U',
            'password': 'StrongPass1!', 'password2': 'StrongPass1!',
            'branch': 'IT', 'year': 3,
        }
        s = RegisterSerializer(data=data)
        s.is_valid()
        user = s.save()
        output = RegisterSerializer(user).data
        assert 'password' not in output
        assert 'password2' not in output


# ============================================================
# UserProfileSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestUserProfileSerializer:
    def test_serializes_user_fields(self, student_user):
        data = UserProfileSerializer(student_user).data
        assert data['email'] == 'student_test@plc.com'
        assert data['role'] == 'student'
        assert data['branch'] == 'CSE'
        assert data['full_name'] == 'Test Student'

    def test_read_only_fields(self, student_user):
        data = UserProfileSerializer(student_user).data
        assert 'id' in data
        assert 'date_joined' in data
        assert 'is_verified' in data


# ============================================================
# CompanyListSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestCompanyListSerializer:
    def test_serializes_company(self, published_company):
        data = CompanyListSerializer(published_company).data
        assert data['name'] == 'Google'
        assert data['hiring_role'] == 'Software Engineer'
        assert data['is_published'] is True

    def test_bookmark_count(self, published_company, student_user):
        from apps.bookmarks.models import Bookmark
        Bookmark.objects.create(user=student_user, company=published_company)
        data = CompanyListSerializer(published_company).data
        assert data['bookmark_count'] == 1

    def test_drive_status(self, published_company, placement_drive):
        data = CompanyListSerializer(published_company).data
        assert data['drive_status'] == 'upcoming'

    def test_no_drive_status(self, db):
        from apps.companies.models import Company
        from django.utils import timezone
        from datetime import timedelta
        c = Company.objects.create(name='NoDrive', deadline=timezone.now() + timedelta(days=1))
        data = CompanyListSerializer(c).data
        assert data['drive_status'] is None


# ============================================================
# CompanyDetailSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestCompanyDetailSerializer:
    def test_includes_drives(self, published_company, placement_drive):
        data = CompanyDetailSerializer(published_company, context={'request': None}).data
        assert 'drives' in data
        assert len(data['drives']) == 1

    def test_is_bookmarked_false_unauthenticated(self, published_company):
        from unittest.mock import MagicMock
        req = MagicMock()
        req.user.is_authenticated = False
        data = CompanyDetailSerializer(published_company, context={'request': req}).data
        assert data['is_bookmarked'] is False

    def test_is_bookmarked_true_for_user(self, published_company, student_user):
        from apps.bookmarks.models import Bookmark
        from unittest.mock import MagicMock
        Bookmark.objects.create(user=student_user, company=published_company)
        req = MagicMock()
        req.user = student_user
        data = CompanyDetailSerializer(published_company, context={'request': req}).data
        assert data['is_bookmarked'] is True


# ============================================================
# PlacementDriveSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestPlacementDriveSerializer:
    def test_serializes_drive(self, placement_drive):
        data = PlacementDriveSerializer(placement_drive).data
        assert data['status'] == 'upcoming'
        assert data['company'] == placement_drive.company.id


# ============================================================
# BookmarkSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestBookmarkSerializer:
    def test_serializes_bookmark_with_company(self, bookmark):
        data = BookmarkSerializer(bookmark).data
        assert 'company' in data
        assert data['company']['name'] == 'Google'
        assert 'created_at' in data


# ============================================================
# AdminStudentSerializer Tests
# ============================================================

@pytest.mark.django_db
class TestAdminStudentSerializer:
    def test_serializes_student(self, student_user):
        data = AdminStudentSerializer(student_user).data
        assert data['email'] == 'student_test@plc.com'
        assert data['full_name'] == 'Test Student'
        assert 'is_verified' in data
        assert 'is_active' in data
