import pytest
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta

from apps.users.models import User, PasswordResetToken
from apps.companies.models import Company, PlacementDrive
from apps.bookmarks.models import Bookmark


# ============================================================
# User Model Tests
# ============================================================

@pytest.mark.django_db
class TestUserModel:
    def test_create_student_user(self):
        user = User.objects.create_user(
            email='u1@test.com', username='u1', password='Pass1234!',
            first_name='A', last_name='B', role='student', branch='CSE', year=4,
        )
        assert user.role == 'student'
        assert user.email == 'u1@test.com'
        assert user.check_password('Pass1234!')
        assert not user.is_verified
        assert user.is_active

    def test_create_admin_user(self):
        user = User.objects.create_user(
            email='adm@test.com', username='adm', password='Pass1234!',
            first_name='Adm', last_name='X', role='admin',
        )
        assert user.role == 'admin'

    def test_full_name_property(self, student_user):
        assert student_user.full_name == 'Test Student'

    def test_str_representation(self, student_user):
        assert str(student_user) == 'Test Student (student_test@plc.com)'

    def test_email_unique_constraint(self, student_user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='student_test@plc.com', username='dupe',
                password='Pass1234!', first_name='D', last_name='U',
            )

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == 'email'

    def test_default_ordering(self, db):
        u1 = User.objects.create_user(email='a@t.com', username='a', password='P1!', first_name='A', last_name='A')
        u2 = User.objects.create_user(email='b@t.com', username='b', password='P1!', first_name='B', last_name='B')
        users = list(User.objects.all())
        assert users[0] == u2  # newest first
        assert users[1] == u1

    def test_branch_choices(self, student_user):
        valid = [c[0] for c in User.BRANCH_CHOICES]
        assert 'CSE' in valid
        assert 'IT' in valid
        assert 'OTHER' in valid

    def test_role_choices(self):
        valid = [c[0] for c in User.ROLE_CHOICES]
        assert 'student' in valid
        assert 'admin' in valid


# ============================================================
# PasswordResetToken Model Tests
# ============================================================

@pytest.mark.django_db
class TestPasswordResetToken:
    def test_token_creation(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        assert token.user == student_user
        assert token.token is not None
        assert not token.is_used
        assert token.expires_at is not None

    def test_token_expiry_default_one_hour(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        expected = timezone.now() + timedelta(hours=1)
        # Allow 2 second tolerance
        assert abs((token.expires_at - expected).total_seconds()) < 2

    def test_token_not_expired(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        assert not token.is_expired

    def test_token_expired(self, student_user):
        token = PasswordResetToken(user=student_user)
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()
        assert token.is_expired

    def test_token_str_representation(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        assert 'student_test@plc.com' in str(token)

    def test_token_unique_uuid(self, student_user):
        t1 = PasswordResetToken.objects.create(user=student_user)
        t2 = PasswordResetToken.objects.create(user=student_user)
        assert t1.token != t2.token

    def test_is_used_flag(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        assert not token.is_used
        token.is_used = True
        token.save()
        token.refresh_from_db()
        assert token.is_used


# ============================================================
# Company Model Tests
# ============================================================

@pytest.mark.django_db
class TestCompanyModel:
    def test_create_company(self, published_company):
        assert published_company.name == 'Google'
        assert published_company.is_published
        assert published_company.views_count == 0

    def test_str_representation(self, published_company):
        assert str(published_company) == 'Google'

    def test_default_ordering(self, db):
        c1 = Company.objects.create(name='A', deadline=timezone.now() + timedelta(days=1))
        c2 = Company.objects.create(name='B', deadline=timezone.now() + timedelta(days=2))
        companies = list(Company.objects.all())
        assert companies[0] == c2  # newest first

    def test_unpublished_company(self, unpublished_company):
        assert not unpublished_company.is_published

    def test_views_count_default_zero(self, published_company):
        assert published_company.views_count == 0

    def test_verbose_name_plural(self):
        assert Company._meta.verbose_name_plural == 'companies'


# ============================================================
# PlacementDrive Model Tests
# ============================================================

@pytest.mark.django_db
class TestPlacementDriveModel:
    def test_create_drive(self, placement_drive, published_company):
        assert placement_drive.company == published_company
        assert placement_drive.status == 'upcoming'

    def test_str_representation(self, placement_drive, published_company):
        expected = f"{published_company.name} - {placement_drive.drive_date}"
        assert str(placement_drive) == expected

    def test_status_choices(self):
        valid = [c[0] for c in PlacementDrive.STATUS_CHOICES]
        assert 'upcoming' in valid
        assert 'ongoing' in valid
        assert 'closed' in valid

    def test_ordering_by_drive_date(self, db, published_company):
        d1 = PlacementDrive.objects.create(
            company=published_company,
            drive_date=(timezone.now() + timedelta(days=20)).date(),
            status='upcoming',
        )
        c2 = Company.objects.create(name='C2', deadline=timezone.now() + timedelta(days=1))
        d2 = PlacementDrive.objects.create(
            company=c2,
            drive_date=(timezone.now() + timedelta(days=5)).date(),
            status='upcoming',
        )
        drives = list(PlacementDrive.objects.all())
        assert drives[0] == d2  # earliest drive first

    def test_cascade_delete_company(self, db):
        c = Company.objects.create(name='Del', deadline=timezone.now() + timedelta(days=1))
        d = PlacementDrive.objects.create(company=c, drive_date=timezone.now().date())
        c.delete()
        assert PlacementDrive.objects.count() == 0


# ============================================================
# Bookmark Model Tests
# ============================================================

@pytest.mark.django_db
class TestBookmarkModel:
    def test_create_bookmark(self, bookmark, student_user, published_company):
        assert bookmark.user == student_user
        assert bookmark.company == published_company

    def test_str_representation(self, bookmark):
        assert 'student_test@plc.com' in str(bookmark)
        assert 'Google' in str(bookmark)

    def test_unique_together_constraint(self, student_user, published_company):
        Bookmark.objects.create(user=student_user, company=published_company)
        with pytest.raises(IntegrityError):
            Bookmark.objects.create(user=student_user, company=published_company)

    def test_ordering(self, student_user, db):
        c1 = Company.objects.create(name='X', deadline=timezone.now() + timedelta(days=1))
        c2 = Company.objects.create(name='Y', deadline=timezone.now() + timedelta(days=2))
        b1 = Bookmark.objects.create(user=student_user, company=c1)
        b2 = Bookmark.objects.create(user=student_user, company=c2)
        bookmarks = list(Bookmark.objects.filter(user=student_user))
        assert bookmarks[0] == b2  # newest first

    def test_cascade_delete_user(self, db, published_company):
        u = User.objects.create_user(email='tmp@t.com', username='tmp', password='P1!')
        Bookmark.objects.create(user=u, company=published_company)
        u.delete()
        assert Bookmark.objects.count() == 0

    def test_cascade_delete_company(self, student_user, db):
        c = Company.objects.create(name='Tmp', deadline=timezone.now() + timedelta(days=1))
        Bookmark.objects.create(user=student_user, company=c)
        c.delete()
        assert Bookmark.objects.count() == 0
