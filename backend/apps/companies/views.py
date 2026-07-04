from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.utils import timezone

from .models import Company, PlacementDrive
from .serializers import (
    CompanyListSerializer, CompanyDetailSerializer,
    CompanyCreateUpdateSerializer, PlacementDriveSerializer,
    PlacementDriveCreateSerializer
)
from apps.users.permissions import IsAdmin


# --- Student-facing views ---

class CompanyListView(generics.ListAPIView):
    """List published companies with search, filter, sort."""
    serializer_class = CompanyListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Company.objects.filter(is_published=True)

        # Search by name
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(name__icontains=search)

        # Filter by drive status
        drive_status = self.request.query_params.get('status', '')
        if drive_status:
            qs = qs.filter(drives__status=drive_status).distinct()

        # Sort
        sort = self.request.query_params.get('sort', 'latest')
        if sort == 'deadline':
            qs = qs.order_by('deadline')
        elif sort == 'name':
            qs = qs.order_by('name')
        else:
            qs = qs.order_by('-created_at')

        return qs


class CompanyDetailView(APIView):
    """Get company detail and increment view count."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            company = Company.objects.get(pk=pk, is_published=True)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Increment view count
        company.views_count = models.F('views_count') + 1
        company.save(update_fields=['views_count'])
        company.refresh_from_db()

        serializer = CompanyDetailSerializer(company, context={'request': request})
        return Response(serializer.data)


# --- Admin views ---

class AdminCompanyListView(generics.ListAPIView):
    """Admin: list all companies (published + drafts)."""
    serializer_class = CompanyListSerializer
    permission_classes = [IsAdmin]
    queryset = Company.objects.all()


class AdminCompanyCreateView(generics.CreateAPIView):
    """Admin: create a new company."""
    serializer_class = CompanyCreateUpdateSerializer
    permission_classes = [IsAdmin]


class AdminCompanyUpdateView(generics.UpdateAPIView):
    """Admin: update a company."""
    serializer_class = CompanyCreateUpdateSerializer
    permission_classes = [IsAdmin]
    queryset = Company.objects.all()
    lookup_field = 'pk'


class AdminCompanyDeleteView(generics.DestroyAPIView):
    """Admin: delete a company."""
    permission_classes = [IsAdmin]
    queryset = Company.objects.all()
    lookup_field = 'pk'


class AdminCompanyPublishToggleView(APIView):
    """Admin: toggle publish status."""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        company.is_published = not company.is_published
        company.save()
        return Response(CompanyListSerializer(company).data)


# --- Placement Drive views ---

class PlacementDriveListView(generics.ListAPIView):
    """List placement drives, optionally filtered by status."""
    serializer_class = PlacementDriveSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = PlacementDrive.objects.select_related('company').all()
        drive_status = self.request.query_params.get('status', '')
        if drive_status:
            qs = qs.filter(status=drive_status)
        return qs


class AdminPlacementDriveCreateView(generics.CreateAPIView):
    """Admin: create a placement drive."""
    serializer_class = PlacementDriveCreateSerializer
    permission_classes = [IsAdmin]


class AdminPlacementDriveUpdateView(generics.UpdateAPIView):
    """Admin: update a placement drive."""
    serializer_class = PlacementDriveCreateSerializer
    permission_classes = [IsAdmin]
    queryset = PlacementDrive.objects.all()
    lookup_field = 'pk'
