from rest_framework import serializers
from .models import Bookmark
from apps.companies.serializers import CompanyListSerializer


class BookmarkSerializer(serializers.ModelSerializer):
    company = CompanyListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ('id', 'company', 'created_at')
