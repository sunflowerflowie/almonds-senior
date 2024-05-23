from django.contrib.auth.models import User
from rest_framework import serializers
from .models import DatabasePlatforms, DatabaseConnections, Roles, DepartmentTags


# Serializer for DatabaseConnections model
class ConnectionSerializer(serializers.ModelSerializer):
    platform_name = serializers.ReadOnlyField(source='platform.platform_name')  # Read-only field to display platform name
    role_name = serializers.ReadOnlyField(source='role.role_name')  # Read-only field to display role name
    department_name = serializers.ReadOnlyField(source='department_tag.department_name')  # Read-only field to display department name

    class Meta:
        model = DatabaseConnections
        fields = [
            "connection_id",
            "database_name",
            "hostname",
            "port",
            "username",
            "password",
            "description",
            "created_by",
            "platform",
            "platform_name",
            "role",
            "role_name",
            "department_tag",
            "department_name"
        ]
        extra_kwargs = {
            "created_by": {"read_only": True},  # created_by field is read-only
            "platform": {"write_only": True},  # platform field is write-only
            "role": {"write_only": True},  # role field is write-only
            "department_tag": {"write_only": True}  # department_tag field is write-only
        }

# Serializer for DatabasePlatforms model
class DatabasePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabasePlatforms
        fields = ['platform_id', 'platform_name']  # Fields to include in the serialization

# Serializer for Roles model
class RolseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['role_id', 'role_name']  # Fields to include in the serialization

# Serializer for DepartmentTags model
class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentTags
        fields = ['department_id', 'department_name']  # Fields to include in the serialization
