from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, NoteSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# API view for creating a new user
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()  # Define the queryset for all User objects
    serializer_class = UserSerializer  # Specify the serializer class to be used
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to access this view
