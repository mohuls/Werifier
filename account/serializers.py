from rest_framework import serializers
from django.contrib.auth.models import User
class UserSeriaizer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()