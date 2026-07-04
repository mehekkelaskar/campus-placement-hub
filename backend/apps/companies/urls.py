from django.urls import path
from .views import (
    CompanyListView, CompanyDetailView,
    AdminCompanyListView, AdminCompanyCreateView,
    AdminCompanyUpdateView, AdminCompanyDeleteView,
    AdminCompanyPublishToggleView,
    PlacementDriveListView,
    AdminPlacementDriveCreateView, AdminPlacementDriveUpdateView
)

urlpatterns = [
    # Student-facing
    path('', CompanyListView.as_view(), name='company-list'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),

    # Placement drives
    path('drives/', PlacementDriveListView.as_view(), name='drive-list'),

    # Admin endpoints
    path('admin/', AdminCompanyListView.as_view(), name='admin-company-list'),
    path('admin/create/', AdminCompanyCreateView.as_view(), name='admin-company-create'),
    path('admin/<int:pk>/update/', AdminCompanyUpdateView.as_view(), name='admin-company-update'),
    path('admin/<int:pk>/delete/', AdminCompanyDeleteView.as_view(), name='admin-company-delete'),
    path('admin/<int:pk>/publish/', AdminCompanyPublishToggleView.as_view(), name='admin-company-publish'),
    path('admin/drives/create/', AdminPlacementDriveCreateView.as_view(), name='admin-drive-create'),
    path('admin/drives/<int:pk>/update/', AdminPlacementDriveUpdateView.as_view(), name='admin-drive-update'),
]
