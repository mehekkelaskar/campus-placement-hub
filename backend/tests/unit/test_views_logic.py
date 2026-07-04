import pytest
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, PasswordResetToken
from apps.companies.models import Company, PlacementDrive
from apps.bookmarks.models import Bookmark


# ============================================================
# View Count Logic Tests
# ============================================================

@pytest.mark.django_db
class TestViewCountLogic:
    def test_view_count_increments(self, published_company):
        assert published_company.views_count == 0
        from django.db import models
        published_company.views_count = models.F('views_count') + 1
        published_company.save(update_fields=['views_count'])
        published_company.refresh_from_db()
        assert published_company.views_count == 1

    def test_view_count_multiple_increments(self, published_company):
        from django.db import models
        for _ in range(5):
            published_company.views_count = models.F('views_count') + 1
            published_company.save(update_fields=['views_count'])
            published_company.refresh_from_db()
        assert published_company.views_count == 5


# ============================================================
# Bookmark Toggle Logic Tests
# ============================================================

@pytest.mark.django_db
class TestBookmarkToggleLogic:
    def test_create_bookmark_on_toggle(self, student_user, published_company):
        bookmark, created = Bookmark.objects.get_or_create(
            user=student_user, company=published_company
        )
        assert created is True
        assert Bookmark.objects.filter(user=student_user, company=published_company).count() == 1

    def test_remove_bookmark_on_second_toggle(self, student_user, published_company):
        Bookmark.objects.get_or_create(user=student_user, company=published_company)
        bookmark, created = Bookmark.objects.get_or_create(
            user=student_user, company=published_company
        )
        if not created:
            bookmark.delete()
        assert Bookmark.objects.filter(user=student_user, company=published_company).count() == 0

    def test_different_users_independent_bookmarks(self, published_company):
        u1 = User.objects.create_user(email='b1@t.com', username='b1', password='P1!')
        u2 = User.objects.create_user(email='b2@t.com', username='b2', password='P1!')
        Bookmark.objects.create(user=u1, company=published_company)
        Bookmark.objects.create(user=u2, company=published_company)
        assert Bookmark.objects.filter(company=published_company).count() == 2


# ============================================================
# Dashboard Aggregation Logic Tests
# ============================================================

@pytest.mark.django_db
class TestDashboardLogic:
    def test_upcoming_drives_count(self, published_company, placement_drive):
        count = PlacementDrive.objects.filter(
            status='upcoming', drive_date__gte=timezone.now().date()
        ).count()
        assert count == 1

    def test_total_published_companies(self, published_company, unpublished_company):
        count = Company.objects.filter(is_published=True).count()
        assert count == 1

    def test_bookmarks_count_for_user(self, student_user, published_company):
        Bookmark.objects.create(user=student_user, company=published_company)
        count = Bookmark.objects.filter(user=student_user).count()
        assert count == 1

    def test_deadline_soon_query(self, db):
        Company.objects.create(
            name='Soon', deadline=timezone.now() + timedelta(days=3),
            is_published=True,
        )
        Company.objects.create(
            name='Far', deadline=timezone.now() + timedelta(days=30),
            is_published=True,
        )
        soon = Company.objects.filter(
            is_published=True,
            deadline__gte=timezone.now(),
            deadline__lte=timezone.now() + timedelta(days=7),
        )
        assert soon.count() == 1
        assert soon.first().name == 'Soon'


# ============================================================
# Admin Dashboard Logic Tests
# ============================================================

@pytest.mark.django_db
class TestAdminDashboardLogic:
    def test_most_bookmarked(self, published_company, student_user):
        from django.db.models import Count
        Bookmark.objects.create(user=student_user, company=published_company)
        result = Company.objects.annotate(
            bookmark_count=Count('bookmarks')
        ).order_by('-bookmark_count').first()
        assert result.bookmark_count == 1

    def test_most_viewed(self, published_company):
        from django.db import models
        published_company.views_count = models.F('views_count') + 10
        published_company.save(update_fields=['views_count'])
        published_company.refresh_from_db()
        top = Company.objects.order_by('-views_count').first()
        assert top.name == 'Google'
        assert top.views_count == 10


# ============================================================
# Chatbot Intent Detection Logic Tests
# ============================================================

@pytest.mark.django_db
class TestChatbotLogic:
    def test_deadline_intent_keywords(self):
        keywords = ['deadline', 'last date', 'due', 'expire']
        question = 'What are the upcoming deadlines?'
        assert any(w in question.lower() for w in keywords)

    def test_interview_intent_keywords(self):
        keywords = ['interview', 'prepar', 'tips', 'how to prepare']
        question = 'How should I prepare for interviews?'
        assert any(w in question.lower() for w in keywords)

    def test_greeting_intent_keywords(self):
        keywords = ['hi', 'hello', 'hey', 'help']
        question = 'Hello there'
        assert any(w in question.lower() for w in keywords)

    def test_company_name_matching(self, published_company):
        question = 'Tell me about Google'
        names = Company.objects.filter(is_published=True).values_list('name', flat=True)
        matched = any(name.lower() in question.lower() for name in names)
        assert matched is True

    def test_no_company_match(self, published_company):
        question = 'Tell me about Netflix'
        names = Company.objects.filter(is_published=True).values_list('name', flat=True)
        matched = any(name.lower() in question.lower() for name in names)
        assert matched is False


# ============================================================
# Placement Drive Status Logic Tests
# ============================================================

@pytest.mark.django_db
class TestDriveStatusLogic:
    def test_upcoming_filter(self, multiple_drives):
        upcoming = PlacementDrive.objects.filter(status='upcoming')
        assert upcoming.count() == 2

    def test_ongoing_filter(self, multiple_drives):
        ongoing = PlacementDrive.objects.filter(status='ongoing')
        assert ongoing.count() == 2

    def test_closed_filter(self, multiple_drives):
        closed = PlacementDrive.objects.filter(status='closed')
        assert closed.count() == 1

    def test_select_related_optimization(self, multiple_drives):
        drives = PlacementDrive.objects.select_related('company').all()
        # Verify select_related doesn't cause errors and returns correct data
        for d in drives:
            assert d.company is not None
            assert d.company.name is not None
