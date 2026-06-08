from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'is_active', 'is_staff']
        read_only_fields = ['is_active', 'is_staff']