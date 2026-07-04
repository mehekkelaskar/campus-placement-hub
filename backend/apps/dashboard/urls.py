from django.urls import path
from .views import StudentDashboardView, AdminDashboardView

urlpatterns = [
    path('', StudentDashboardView.as_view(), name='student-dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
]
