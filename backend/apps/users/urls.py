from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, MeView,
    ForgotPasswordView, ResetPasswordView, AIChatbotView,
    AdminStudentListView, AdminStudentVerifyView,
    AdminStudentToggleActiveView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),

    # Password reset
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # AI Chatbot
    path('chatbot/', AIChatbotView.as_view(), name='chatbot'),

    # Admin endpoints
    path('admin/students/', AdminStudentListView.as_view(), name='admin-students'),
    path('admin/students/<int:pk>/verify/', AdminStudentVerifyView.as_view(), name='admin-student-verify'),
    path('admin/students/<int:pk>/toggle-active/', AdminStudentToggleActiveView.as_view(), name='admin-student-toggle'),
]
