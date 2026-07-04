from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'branch', 'is_verified', 'is_active')
    list_filter = ('role', 'branch', 'is_verified', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'branch', 'year', 'phone', 'avatar', 'is_verified')}),
    )
