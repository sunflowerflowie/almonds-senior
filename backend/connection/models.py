from django.db import models
from django.contrib.auth.models import User


# Model to represent different database platforms
class DatabasePlatforms(models.Model):
    platform_id = models.AutoField(primary_key=True)  # Primary key for the platform
    platform_name = models.CharField(unique=True, max_length=255)  # Unique name for the platform

    def __str__(self):
        return self.platform_name  # String representation of the model

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'database_platforms'  # Custom table name in the database

# Model to represent database connections
class DatabaseConnections(models.Model):
    connection_id = models.AutoField(primary_key=True)  # Primary key for the connection
    database_name = models.CharField(max_length=255)  # Name of the database
    hostname = models.CharField(max_length=255)  # Hostname of the database server
    port = models.IntegerField()  # Port number for the database connection
    username = models.CharField(max_length=255)  # Username for the database connection
    password = models.CharField(max_length=255)  # Password for the database connection
    description = models.TextField(blank=True, null=True)  # Optional description of the connection
    created_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, db_column='created_by_user_id')  # User who created the connection
    platform = models.ForeignKey('DatabasePlatforms', models.DO_NOTHING, blank=True, null=True)  # Foreign key to the database platform
    role = models.ForeignKey('Roles', models.DO_NOTHING, blank=True, null=True)  # Foreign key to the role
    department_tag = models.ForeignKey('DepartmentTags', models.DO_NOTHING, blank=True, null=True)  # Foreign key to the department tag

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'database_connections'  # Custom table name in the database

# Model to represent different roles
class Roles(models.Model):
    role_id = models.AutoField(primary_key=True)  # Primary key for the role
    role_name = models.CharField(unique=True, max_length=255)  # Unique name for the role

    def __str__(self):
        return self.role_name  # String representation of the model

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'roles'  # Custom table name in the database

# Model to represent department tags
class DepartmentTags(models.Model):
    department_id = models.AutoField(primary_key=True)  # Primary key for the department tag
    department_name = models.CharField(unique=True, max_length=255)  # Unique name for the department

    def __str__(self):
        return self.department_name  # String representation of the model

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'department_tags'  # Custom table name in the database
