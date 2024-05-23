from django.urls import path
from .views import get_tables_for_connection, get_attributes_for_table, update_attribute_details


# Define URL patterns for the application's API endpoints
urlpatterns = [
    path('tables/<int:connection_id>/', get_tables_for_connection, name='database-tables'),  # URL for fetching tables for a specific connection
    path('attributes/<int:connection_id>/<str:table_name>/', get_attributes_for_table, name='table-attributes'),  # URL for fetching attributes for a specific table in a connection
    path('update/<int:attribute_id>/', update_attribute_details, name='update'),  # URL for updating details of a specific attribute
]
