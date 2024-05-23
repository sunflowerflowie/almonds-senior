from django.db import models
from django.contrib.auth.models import User
from connection.models import DatabaseConnections


# Model to represent data tables within a database connection
class DataTables(models.Model):
    table_id = models.AutoField(primary_key=True)  # Primary key for the table
    table_name = models.CharField(max_length=255)  # Name of the table
    connection = models.ForeignKey('connection.DatabaseConnections', models.DO_NOTHING, blank=True, null=True)  # Foreign key to the database connection

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'data_tables'  # Custom table name in the database

# Model to represent attributes (columns) of data tables
class AssetAttributes(models.Model):
    attribute_id = models.AutoField(primary_key=True)  # Primary key for the attribute
    attribute_name = models.CharField(max_length=255)  # Name of the attribute
    data_type = models.CharField(max_length=255)  # Data type of the attribute
    is_primary_key = models.BooleanField()  # Indicates if the attribute is a primary key
    is_foreign_key = models.BooleanField()  # Indicates if the attribute is a foreign key
    description = models.TextField(blank=True, null=True)  # Optional description of the attribute
    table = models.ForeignKey('DataTables', models.DO_NOTHING, blank=True, null=True)  # Foreign key to the data table

    class Meta:
        managed = True  # Django will manage the database table's lifecycle
        db_table = 'asset_attributes'  # Custom table name in the database
