from rest_framework import serializers
from .models import Company, PlacementDrive


class PlacementDriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDrive
        fields = '__all__'


class CompanyListSerializer(serializers.ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()
    drive_status = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ('id', 'name', 'logo', 'hiring_role', 'deadline',
                  'is_published', 'views_count', 'created_at',
                  'bookmark_count', 'drive_status')

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count() if hasattr(obj, 'bookmarks') else 0

    def get_drive_status(self, obj):
        drive = obj.drives.order_by('-drive_date').first()
        return drive.status if drive else None


class CompanyDetailSerializer(serializers.ModelSerializer):
    drives = PlacementDriveSerializer(many=True, read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False


class CompanyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class PlacementDriveCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDrive
        fields = '__all__'
