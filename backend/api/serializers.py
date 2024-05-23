from django.contrib.auth.models import User
from rest_framework import serializers


# Serializer for User model, converting User instances to JSON and vice versa
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]  # Specify fields to include in the serialization
        extra_kwargs = {"password": {"write_only": True}}  # Ensure password is write-only and not exposed in API responses

    # Overriding the create method to handle password hashing
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # Create user with hashed password
        return user

