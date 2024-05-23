from django.shortcuts import render
from rest_framework import generics
from .serializers import ConnectionSerializer, DatabasePlatformSerializer, RolseSerializer, DepartmentsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import DatabasePlatforms, DatabaseConnections, Roles, DepartmentTags


# API view to list all database platforms
class DatabasePlatformList(generics.ListAPIView):
    queryset = DatabasePlatforms.objects.all()  # Queryset of all database platforms
    serializer_class = DatabasePlatformSerializer  # Serializer to use for the queryset

# API view to list all roles
class RoleList(generics.ListAPIView):
    queryset = Roles.objects.all()  # Queryset of all roles
    serializer_class = RolseSerializer  # Serializer to use for the queryset

# API view to list all department tags
class DepartmentTagList(generics.ListAPIView):
    queryset = DepartmentTags.objects.all()  # Queryset of all department tags
    serializer_class = DepartmentsSerializer  # Serializer to use for the queryset

# API view to list and create database connections
class ConnectionListCreate(generics.ListCreateAPIView):
    serializer_class = ConnectionSerializer  # Serializer to use for the queryset
    permission_classes = [IsAuthenticated]  # Require user to be authenticated to access this view

    def get_queryset(self):
        user = self.request.user  # Get the current authenticated user
        return DatabaseConnections.objects.filter(created_by=user)  # Return connections created by the current user

    def perform_create(self, serializer):
        if serializer.is_valid():  # Check if the serializer data is valid
            serializer.save(created_by=self.request.user)  # Save the connection with the current user as creator
        else:
            print(serializer.errors)  # Print any errors if the data is not valid

# API view to delete a specific database connection
class ConnectionDelete(generics.DestroyAPIView):
    queryset = DatabaseConnections.objects.all()  # Queryset of all database connections
    serializer_class = ConnectionSerializer  # Serializer to use for the queryset
    permission_classes = [IsAuthenticated]  # Require user to be authenticated to access this view

    def get_queryset(self):
        user = self.request.user  # Get the current authenticated user
        return DatabaseConnections.objects.filter(created_by=user)  # Return connections created by the current user
