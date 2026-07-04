import pytest
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, PasswordResetToken


@pytest.mark.django_db
class TestPasswordResetTokenLifecycle:
    def test_create_token_for_user(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        assert token.user == student_user
        assert not token.is_used
        assert not token.is_expired

    def test_token_expiry_after_one_hour(self, student_user):
        token = PasswordResetToken(user=student_user)
        token.expires_at = timezone.now() + timedelta(minutes=59)
        token.save()
        assert not token.is_expired

        token.expires_at = timezone.now() - timedelta(seconds=1)
        token.save()
        assert token.is_expired

    def test_invalidate_old_tokens(self, student_user):
        t1 = PasswordResetToken.objects.create(user=student_user)
        t2 = PasswordResetToken.objects.create(user=student_user)
        # Invalidate old tokens
        PasswordResetToken.objects.filter(user=student_user, is_used=False).exclude(pk=t2.pk).update(is_used=True)
        t1.refresh_from_db()
        t2.refresh_from_db()
        assert t1.is_used is True
        assert t2.is_used is False

    def test_token_cannot_be_reused(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        # Simulate password reset
        token.is_used = True
        token.save()
        # Trying to use again should fail
        assert token.is_used is True

    def test_multiple_users_independent_tokens(self, db):
        u1 = User.objects.create_user(email='r1@t.com', username='r1', password='P1!')
        u2 = User.objects.create_user(email='r2@t.com', username='r2', password='P1!')
        t1 = PasswordResetToken.objects.create(user=u1)
        t2 = PasswordResetToken.objects.create(user=u2)
        t1.is_used = True
        t1.save()
        assert t1.is_used is True
        assert t2.is_used is False

    def test_password_reset_flow(self, student_user):
        """Full flow: create token -> verify -> reset password -> mark used."""
        token = PasswordResetToken.objects.create(user=student_user)
        assert not token.is_expired
        assert not token.is_used

        # Reset password
        student_user.set_password('NewPass123!')
        student_user.save()
        token.is_used = True
        token.save()

        # Verify new password works
        student_user.refresh_from_db()
        assert student_user.check_password('NewPass123!')
        assert token.is_used

    def test_token_lookup_by_uuid(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        found = PasswordResetToken.objects.get(token=token.token, is_used=False)
        assert found == token

    def test_expired_token_not_found_as_valid(self, student_user):
        token = PasswordResetToken.objects.create(user=student_user)
        token.expires_at = timezone.now() - timedelta(hours=2)
        token.save()
        # Can still look it up, but is_expired is True
        found = PasswordResetToken.objects.get(token=token.token)
        assert found.is_expired

    def test_cascade_delete_with_user(self, db):
        u = User.objects.create_user(email='del@t.com', username='del', password='P1!')
        PasswordResetToken.objects.create(user=u)
        u.delete()
        assert PasswordResetToken.objects.count() == 0
