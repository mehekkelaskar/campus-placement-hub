import pytest
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.companies.models import Company, PlacementDrive
from apps.bookmarks.models import Bookmark
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def student_user(db):
    """Create a standard student user."""
    user = User.objects.create_user(
        email='student_test@plc.com',
        username='student_test',
        password='TestPass123!',
        first_name='Test',
        last_name='Student',
        role='student',
        branch='CSE',
        year=4,
        phone='1234567890',
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User.objects.create_user(
        email='admin_test@plc.com',
        username='admin_test',
        password='AdminPass123!',
        first_name='Test',
        last_name='Admin',
        role='admin',
    )
    return user


@pytest.fixture
def verified_student(db):
    """Create a verified student user."""
    user = User.objects.create_user(
        email='verified@plc.com',
        username='verified_student',
        password='TestPass123!',
        first_name='Verified',
        last_name='Student',
        role='student',
        branch='CSE',
        year=4,
        is_verified=True,
    )
    return user


@pytest.fixture
def inactive_student(db):
    """Create an inactive student user."""
    user = User.objects.create_user(
        email='inactive@plc.com',
        username='inactive_student',
        password='TestPass123!',
        first_name='Inactive',
        last_name='Student',
        role='student',
        branch='IT',
        year=3,
    )
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def student_token(student_user):
    """Return JWT access token for student_user."""
    refresh = RefreshToken.for_user(student_user)
    return str(refresh.access_token)


@pytest.fixture
def student_tokens(student_user):
    """Return both JWT tokens for student_user."""
    refresh = RefreshToken.for_user(student_user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def admin_token(admin_user):
    """Return JWT access token for admin_user."""
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)


@pytest.fixture
def admin_tokens(admin_user):
    """Return both JWT tokens for admin_user."""
    refresh = RefreshToken.for_user(admin_user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def published_company(db):
    """Create a published company with deadline in future."""
    return Company.objects.create(
        name='Google',
        about='A leading technology company.',
        hiring_role='Software Engineer',
        eligibility='CGPA >= 7.0, CSE/IT branches',
        apply_link='https://careers.google.com/apply',
        website='https://google.com',
        deadline=timezone.now() + timedelta(days=30),
        recruitment_process='Online Test -> Technical Interview -> HR Interview',
        is_published=True,
    )


@pytest.fixture
def unpublished_company(db):
    """Create an unpublished (draft) company."""
    return Company.objects.create(
        name='Draft Corp',
        about='A draft company.',
        hiring_role='Data Analyst',
        deadline=timezone.now() + timedelta(days=15),
        is_published=False,
    )


@pytest.fixture
def multiple_companies(db):
    """Create multiple published companies for listing tests."""
    companies = []
    names = ['Microsoft', 'Amazon', 'TCS', 'Infosys', 'Meta']
    roles = ['SDE', 'SDE-1', 'Digital Engineer', 'Systems Engineer', 'SWE']
    for i, (name, role) in enumerate(zip(names, roles)):
        c = Company.objects.create(
            name=name,
            hiring_role=role,
            deadline=timezone.now() + timedelta(days=(i + 1) * 5),
            is_published=True,
        )
        companies.append(c)
    return companies


@pytest.fixture
def placement_drive(db, published_company):
    """Create a placement drive for the published company."""
    return PlacementDrive.objects.create(
        company=published_company,
        drive_date=(timezone.now() + timedelta(days=10)).date(),
        test_date=(timezone.now() + timedelta(days=5)).date(),
        interview_date=(timezone.now() + timedelta(days=8)).date(),
        status='upcoming',
        notes='Main campus drive',
    )


@pytest.fixture
def multiple_drives(db, multiple_companies):
    """Create multiple drives with different statuses."""
    drives = []
    statuses = ['upcoming', 'ongoing', 'closed', 'upcoming', 'ongoing']
    for company, status in zip(multiple_companies, statuses):
        d = PlacementDrive.objects.create(
            company=company,
            drive_date=(timezone.now() + timedelta(days=10)).date(),
            status=status,
        )
        drives.append(d)
    return drives


@pytest.fixture
def bookmark(db, student_user, published_company):
    """Create a bookmark for student_user on published_company."""
    return Bookmark.objects.create(user=student_user, company=published_company)


@pytest.fixture
def auth_client(db, student_token):
    """Return APIClient authenticated as student."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
    return client


@pytest.fixture
def admin_client(db, admin_token):
    """Return APIClient authenticated as admin."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    return client


@pytest.fixture
def anon_client(db):
    """Return unauthenticated APIClient."""
    from rest_framework.test import APIClient
    return APIClient()
