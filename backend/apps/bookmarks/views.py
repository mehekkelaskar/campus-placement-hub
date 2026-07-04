from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.models import Company
from .models import Bookmark
from .serializers import BookmarkSerializer


class BookmarkListView(generics.ListAPIView):
    """List current user's bookmarks."""
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('company')


class BookmarkToggleView(APIView):
    """Toggle bookmark for a company (add if not exists, remove if exists)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, company_id):
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user, company=company
        )

        if not created:
            # Already bookmarked, remove it
            bookmark.delete()
            return Response({'bookmarked': False}, status=status.HTTP_200_OK)

        return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)
