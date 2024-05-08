import psycopg2
from psycopg2.extras import DictCursor
from django.db import transaction
from connection.models import DatabaseConnections
from .models import DataTables, AssetAttributes

"""
Handles the creation of a database connection.
"""
def create_database_connection(connection):
    try:
        conn = psycopg2.connect(
            dbname=connection.database_name,
            user=connection.username,
            password=connection.password,
            host=connection.hostname,
            port=connection.port
        )

        return conn
    except Exception as e:
        print(f"Error connecting to database {connection.database_name}: {e}")

        return None

def fetch_table_names(conn):
    if conn is not None:
        cursor = conn.cursor()
        # Modify the query to only select tables and exclude views or other types
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        table_names = cursor.fetchall()
        cursor.close()

        return table_names
    
    return []

"""
Saves fetched table names into the DataTables model.
"""
def store_table_names(table_names, connection):
    with transaction.atomic():
        for table_name in table_names:
            DataTables.objects.update_or_create(
                table_name=table_name[0],  # table_name is a tuple
                connection=connection,
                defaults={'table_name': table_name[0]}
            )

"""
Update data tables from all database connections.
"""
def update_data_tables():
    connections = DatabaseConnections.objects.all()
    for connection in connections:
        conn = create_database_connection(connection)
        table_names = fetch_table_names(conn)
        if table_names:
            store_table_names(table_names, connection)

"""
Query for reset AutoField:
ALTER SEQUENCE data_tables_table_id_seq RESTART WITH 1;
"""

"""
Fetch all attributes for a given table.
"""
def fetch_table_attributes(conn, table_name):
    attributes = []
    query = """
    SELECT
        c.column_name, 
        c.data_type,
        (EXISTS (
            SELECT 1 
            FROM pg_index AS pi
            JOIN pg_attribute AS pa ON pa.attrelid = pi.indrelid AND pa.attnum = ANY(pi.indkey)
            WHERE pi.indrelid = cl.oid AND pi.indisprimary AND pa.attname = c.column_name
        )) AS is_primary_key,
        EXISTS (
            SELECT 1 
            FROM pg_constraint 
            WHERE conrelid = cl.oid 
            AND conkey = ARRAY[a.attnum] 
            AND contype = 'f'
        ) AS is_foreign_key
    FROM 
        information_schema.columns AS c
        JOIN pg_class AS cl ON cl.relname = c.table_name AND cl.relkind = 'r'
        JOIN pg_namespace AS n ON cl.relnamespace = n.oid AND n.nspname = c.table_schema
        LEFT JOIN pg_attribute AS a ON a.attrelid = cl.oid AND a.attname = c.column_name
    WHERE 
        c.table_name = %s
        AND c.table_schema = 'public';  -- Replace 'public' with a variable if needed
    """
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (table_name,))
            attributes = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching attributes for table {table_name}: {e}")
    return attributes

"""
Store these attributes in the AssetAttributes model.
"""
def store_table_attributes(table_name, attributes, connection):
    attribute_ids = []
    
    try:
        table = DataTables.objects.get(table_name=table_name, connection=connection)
        with transaction.atomic():
            # for attr in attributes:
            #     AssetAttributes.objects.update_or_create(
            #         attribute_name=attr['column_name'],
            #         table=table,
            #         defaults={
            #             'attribute_name': attr['column_name'],
            #             'data_type': attr['data_type'],
            #             'is_primary_key': attr['is_primary_key'],
            #             'is_foreign_key': attr['is_foreign_key'],
            #             'description': '',
            #         }
            #     )
            for attr in attributes:
                asset_attr, created = AssetAttributes.objects.update_or_create(
                    attribute_name=attr['column_name'],
                    table=table,
                    defaults={
                        'attribute_name': attr['column_name'],
                        'data_type': attr['data_type'],
                        'is_primary_key': attr['is_primary_key'],
                        'is_foreign_key': attr['is_foreign_key'],
                        'description': '',
                    }
                )
                attribute_ids.append(asset_attr.attribute_id)
    except DataTables.DoesNotExist:
        print(f"No table found with name {table_name} and connection {connection}")
    return attribute_ids

"""

"""
def update_data_tables_and_attributes():
    connections = DatabaseConnections.objects.all()
    for connection in connections:
        conn = create_database_connection(connection)
        try:
            if conn:
                table_names = fetch_table_names(conn)
                if table_names:
                    store_table_names(table_names, connection)
                    for table_name in table_names:
                        attributes = fetch_table_attributes(conn, table_name[0])
                        if attributes:
                            store_table_attributes(table_name[0], attributes, connection)
        finally:
            if conn:
                conn.close()
