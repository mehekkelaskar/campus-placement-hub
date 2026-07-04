from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from django.contrib.auth import authenticate

from .models import User, PasswordResetToken
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    UserUpdateSerializer, AdminStudentSerializer
)
from .permissions import IsAdmin


class RegisterView(generics.CreateAPIView):
    """Student registration."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login with JWT."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is deactivated. Contact admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class MeView(APIView):
    """Get or update current user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


class AdminStudentListView(generics.ListAPIView):
    """Admin: list all students."""
    serializer_class = AdminStudentSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = User.objects.filter(role='student')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(username__icontains=search)
            )
        branch = self.request.query_params.get('branch', '')
        if branch:
            qs = qs.filter(branch=branch)
        return qs


class AdminStudentVerifyView(APIView):
    """Admin: verify/unverify a student."""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            student = User.objects.get(pk=pk, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        student.is_verified = not student.is_verified
        student.save()
        return Response(AdminStudentSerializer(student).data)


class AdminStudentToggleActiveView(APIView):
    """Admin: activate/deactivate a student."""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            student = User.objects.get(pk=pk, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        student.is_active = not student.is_active
        student.save()
        return Response(AdminStudentSerializer(student).data)


# --- Forgot Password ---

class ForgotPasswordView(APIView):
    """Request a password reset token."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Please provide your email address.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            return Response({
                'message': 'If an account with that email exists, a reset link has been sent.',
                'reset_token': None
            })

        # Invalidate old tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        reset_token = PasswordResetToken.objects.create(user=user)

        # In production, this would be sent via email.
        # For demo, we return the token directly.
        return Response({
            'message': 'If an account with that email exists, a reset link has been sent.',
            'reset_token': str(reset_token.token),
            'expires_in': '1 hour'
        })


class ResetPasswordView(APIView):
    """Reset password using token."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if not token or not password or not password2:
            return Response(
                {'error': 'Token and both password fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password2:
            return Response(
                {'error': 'Passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if reset_token.is_expired:
            return Response(
                {'error': 'Reset token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user = reset_token.user
        user.set_password(password)
        user.save()

        # Mark token as used
        reset_token.is_used = True
        reset_token.save()

        return Response({
            'message': 'Password has been reset successfully. You can now log in.'
        })


# --- AI Chatbot ---

class AIChatbotView(APIView):
    """AI assistant for placement-related queries."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.companies.models import Company, PlacementDrive
        from django.db.models import Count

        question = request.data.get('question', '').strip().lower()

        if not question:
            return Response({
                'reply': "Hi! I'm your placement assistant. Ask me anything about companies, deadlines, eligibility, or preparation tips!"
            })

        # Intent detection + response generation
        reply = self._generate_reply(question)
        return Response({'reply': reply})

    def _generate_reply(self, question):
        from apps.companies.models import Company, PlacementDrive
        from django.db.models import Count
        from django.utils import timezone

        # Company-specific queries
        company_names = Company.objects.filter(is_published=True).values_list('name', flat=True)
        matched_company = None
        for name in company_names:
            if name.lower() in question:
                matched_company = Company.objects.get(name=name)
                break

        if matched_company:
            return self._company_info(matched_company, question)

        # Deadline related
        if any(w in question for w in ['deadline', 'last date', 'due', 'expire']):
            now = timezone.now()
            upcoming = Company.objects.filter(
                is_published=True, deadline__gte=now
            ).order_by('deadline')[:5]
            if upcoming:
                lines = ["Here are the upcoming deadlines:"]
                for c in upcoming:
                    from datetime import timedelta
                    days_left = (c.deadline - now).days
                    lines.append(f"  - {c.name} ({c.hiring_role}): {c.deadline.strftime('%b %d, %Y')} ({days_left} days left)")
                return "\n".join(lines)
            return "No upcoming deadlines at the moment. Check back later!"

        # Eligibility
        if any(w in question for w in ['eligib', 'criteria', 'requirement', 'cgpa', 'gpa']):
            companies = Company.objects.filter(is_published=True, eligibility__isnull=False).exclude(eligibility='')[:5]
            if companies:
                lines = ["Here are eligibility criteria for current openings:"]
                for c in companies:
                    lines.append(f"  - {c.name}: {c.eligibility}")
                return "\n".join(lines)
            return "No eligibility information available right now."

        # Upcoming drives
        if any(w in question for w in ['drive', 'upcoming', 'schedule', 'when']):
            drives = PlacementDrive.objects.filter(
                status='upcoming'
            ).select_related('company').order_by('drive_date')[:5]
            if drives:
                lines = ["Upcoming placement drives:"]
                for d in drives:
                    lines.append(f"  - {d.company.name}: Drive on {d.drive_date.strftime('%b %d, %Y')}" +
                               (f" | Test: {d.test_date.strftime('%b %d')}" if d.test_date else "") +
                               (f" | Interview: {d.interview_date.strftime('%b %d')}" if d.interview_date else ""))
                return "\n".join(lines)
            return "No upcoming drives scheduled at the moment."

        # Popular companies
        if any(w in question for w in ['popular', 'top', 'best', 'most', 'which compan']):
            top = Company.objects.filter(is_published=True).order_by('-views_count')[:5]
            if top:
                lines = ["Most popular companies on the portal:"]
                for c in top:
                    lines.append(f"  - {c.name} ({c.hiring_role}) - {c.views_count} views")
                return "\n".join(lines)
            return "No company data available yet."

        # Interview preparation tips
        if any(w in question for w in ['interview', 'prepar', 'tips', 'how to prepare']):
            return (
                "Here are some interview preparation tips:\n\n"
                "1. Research the company thoroughly - know their products, culture, and recent news\n"
                "2. Practice DSA problems on LeetCode/HackerRank (focus on arrays, strings, trees, DP)\n"
                "3. Prepare your project explanations - be ready to discuss 2-3 projects in depth\n"
                "4. Practice system design basics for senior roles\n"
                "5. Prepare behavioral questions using the STAR method\n"
                "6. Review your resume - be ready to explain every point\n"
                "7. Mock interviews with friends help build confidence\n\n"
                "Ask me about a specific company and I'll give you tailored advice!"
            )

        # Resume tips
        if any(w in question for w in ['resume', 'cv', 'profile']):
            return (
                "Resume tips for placements:\n\n"
                "1. Keep it to 1 page (freshers) or 2 pages max\n"
                "2. Lead with skills and projects, then education\n"
                "3. Quantify achievements (e.g., 'improved performance by 40%')\n"
                "4. Include relevant GitHub/portfolio links\n"
                "5. Use action verbs: Built, Developed, Optimized, Led\n"
                "6. No spelling errors - proofread multiple times\n"
                "7. Tailor your resume for each role when possible"
            )

        # Greeting
        if any(w in question for w in ['hi', 'hello', 'hey', 'help']):
            return (
                "Hello! I'm your placement assistant. I can help you with:\n\n"
                "- Company information (ask about any company on the portal)\n"
                "- Upcoming deadlines and placement drives\n"
                "- Eligibility criteria for companies\n"
                "- Interview preparation tips\n"
                "- Resume advice\n"
                "- Popular companies and trends\n\n"
                "Just ask your question and I'll do my best to help!"
            )

        # Thank you
        if any(w in question for w in ['thanks', 'thank you', 'thx']):
            return "You're welcome! Feel free to ask anything else. Good luck with your placements! :)"

        # Default fallback
        return (
            "I'm not sure about that specific question, but here's what I can help with:\n\n"
            "- Ask about any company on the portal (e.g., 'Tell me about Google')\n"
            "- Check deadlines ('What are the upcoming deadlines?')\n"
            "- View placement drives ('What drives are coming up?')\n"
            "- Get interview tips ('How should I prepare for interviews?')\n"
            "- Resume advice ('Any tips for my resume?')\n"
            "- Eligibility info ('What are the eligibility criteria?')\n\n"
            "Try asking one of these!"
        )

    def _company_info(self, company, question):
        """Generate company-specific response."""
        from django.utils import timezone
        from datetime import timedelta

        info = [f"Here's what I know about {company.name}:"]

        if company.hiring_role:
            info.append(f"  Hiring Role: {company.hiring_role}")
        if company.eligibility:
            info.append(f"  Eligibility: {company.eligibility}")
        if company.deadline:
            now = timezone.now()
            days_left = (company.deadline - now).days
            status = f"{days_left} days left" if days_left > 0 else "Deadline passed"
            info.append(f"  Deadline: {company.deadline.strftime('%b %d, %Y')} ({status})")
        if company.recruitment_process:
            info.append(f"  Recruitment Process:\n    {company.recruitment_process}")
        if company.about:
            info.append(f"  About: {company.about[:200]}...")

        # Preparation tips specific to this company
        if any(w in question for w in ['prepar', 'interview', 'tips', 'how']):
            info.append(f"\n  Preparation tips for {company.name}:")
            info.append("  - Research their recent products and news")
            info.append("  - Practice company-specific coding problems")
            info.append("  - Understand their tech stack")
            info.append("  - Prepare questions about their work culture")

        return "\n".join(info)
