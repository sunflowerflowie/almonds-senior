from django.urls import path
from . import views

# Define URL patterns for the application's API endpoints
urlpatterns = [
    path("forms/", views.ConnectionListCreate.as_view(), name="connection-list"),  # URL pattern for listing and creating database connections
    path("forms/delete/<int:pk>/", views.ConnectionDelete.as_view(), name="delete-connection"),  # URL pattern for deleting a specific database connection identified by its primary key
    path("platforms/", views.DatabasePlatformList.as_view(), name="platform-list"),  # URL pattern for listing all database platforms
    path("roles/", views.RoleList.as_view(), name="role-list"),  # URL pattern for listing all roles
    path("departments/", views.DepartmentTagList.as_view(), name="department-list"),  # URL pattern for listing all department tags
]
