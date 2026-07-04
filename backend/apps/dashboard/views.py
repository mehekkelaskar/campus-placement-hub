from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from apps.companies.models import Company, PlacementDrive
from apps.bookmarks.models import Bookmark
from apps.users.models import User


class StudentDashboardView(APIView):
    """Aggregated dashboard data for students."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        user = request.user

        # Upcoming drives (next 30 days)
        upcoming_drives = PlacementDrive.objects.filter(
            status='upcoming',
            drive_date__gte=now.date()
        ).select_related('company').order_by('drive_date')[:5]

        # Recently added companies (last 10 published)
        recent_companies = Company.objects.filter(
            is_published=True
        ).order_by('-created_at')[:5]

        # Approaching deadlines (next 7 days)
        deadline_soon = Company.objects.filter(
            is_published=True,
            deadline__gte=now,
            deadline__lte=now + timedelta(days=7)
        ).order_by('deadline')[:5]

        # User's bookmarks count
        bookmarks_count = Bookmark.objects.filter(user=user).count()

        # Total published companies
        total_companies = Company.objects.filter(is_published=True).count()

        # Upcoming drives count
        upcoming_count = PlacementDrive.objects.filter(
            status='upcoming', drive_date__gte=now.date()
        ).count()

        upcoming_drives_data = []
        for drive in upcoming_drives:
            upcoming_drives_data.append({
                'id': drive.id,
                'company_name': drive.company.name,
                'company_logo': drive.company.logo.url if drive.company.logo else None,
                'drive_date': drive.drive_date,
                'test_date': drive.test_date,
                'interview_date': drive.interview_date,
                'status': drive.status,
            })

        recent_companies_data = []
        for c in recent_companies:
            recent_companies_data.append({
                'id': c.id,
                'name': c.name,
                'logo': c.logo.url if c.logo else None,
                'hiring_role': c.hiring_role,
                'deadline': c.deadline,
            })

        deadline_soon_data = []
        for c in deadline_soon:
            deadline_soon_data.append({
                'id': c.id,
                'name': c.name,
                'logo': c.logo.url if c.logo else None,
                'hiring_role': c.hiring_role,
                'deadline': c.deadline,
            })

        return Response({
            'stats': {
                'total_companies': total_companies,
                'upcoming_drives': upcoming_count,
                'bookmarks': bookmarks_count,
            },
            'upcoming_drives': upcoming_drives_data,
            'recent_companies': recent_companies_data,
            'approaching_deadlines': deadline_soon_data,
        })


class AdminDashboardView(APIView):
    """Aggregated dashboard data for admin."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required.'}, status=403)

        now = timezone.now()

        total_companies = Company.objects.count()
        published_companies = Company.objects.filter(is_published=True).count()
        total_students = User.objects.filter(role='student').count()
        verified_students = User.objects.filter(role='student', is_verified=True).count()
        active_drives = PlacementDrive.objects.filter(status='upcoming').count()
        total_bookmarks = Bookmark.objects.count()

        # Most bookmarked companies
        from django.db.models import Count
        most_bookmarked = Company.objects.annotate(
            bookmark_count=Count('bookmarks')
        ).order_by('-bookmark_count')[:5].values('id', 'name', 'bookmark_count')

        # Most viewed companies
        most_viewed = Company.objects.order_by('-views_count')[:5].values(
            'id', 'name', 'views_count'
        )

        return Response({
            'stats': {
                'total_companies': total_companies,
                'published_companies': published_companies,
                'total_students': total_students,
                'verified_students': verified_students,
                'active_drives': active_drives,
                'total_bookmarks': total_bookmarks,
            },
            'most_bookmarked': list(most_bookmarked),
            'most_viewed': list(most_viewed),
        })
