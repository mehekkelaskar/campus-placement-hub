from django.contrib import admin
from .models import Company, PlacementDrive


class PlacementDriveInline(admin.TabularInline):
    model = PlacementDrive
    extra = 1


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'hiring_role', 'deadline', 'is_published', 'views_count', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('name', 'hiring_role')
    list_editable = ('is_published',)
    inlines = [PlacementDriveInline]


@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ('company', 'drive_date', 'test_date', 'interview_date', 'status')
    list_filter = ('status', 'drive_date')
    search_fields = ('company__name',)
