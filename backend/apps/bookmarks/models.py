from django.db import models
from django.conf import settings
from apps.companies.models import Company


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='bookmarks')
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.company.name}"
