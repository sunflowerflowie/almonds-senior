import psycopg2
import pymysql
import os
from pymongo import MongoClient
from psycopg2.extras import DictCursor
from django.db import transaction
from connection.models import DatabaseConnections
from .models import DataTables, AssetAttributes
from django.conf import settings


"""
Handles the creation of a database connection.
"""
def create_database_connection(connection):
    try:
        if connection.platform.platform_id == 1:
            conn = psycopg2.connect(
                dbname=connection.database_name,
                user=connection.username,
                password=connection.password,
                host=connection.hostname,
                port=connection.port
            )

            return conn,connection.platform.platform_id
        elif connection.platform.platform_id == 2:

            connect_mysql = pymysql.connect(
                host=connection.hostname,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database_name
            )

            return connect_mysql,connection.platform.platform_id
        elif connection.platform.platform_id == 3:
            client = MongoClient(os.getenv("DB_URL_MONGO"))
            db_mongo = client[connection.database_name]
            return db_mongo,connection.platform.platform_id
       
    except Exception as e:
        print(f"Error connecting to database {connection.database_name}: {e}")

        return None,connection.platform.platform_id

def fetch_table_names(db,platform_id):
        if db is None:
            return []
        
        if platform_id == 1 or platform_id == 2:
            cursor = db.cursor()
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE'
            """
            schema = 'public' if platform_id == 1 else os.getenv("DB_NAME_MYSQL")
            cursor.execute(query, [schema])
            table_names = cursor.fetchall()
            cursor.close()
            return table_names
        
        elif platform_id == 3:
            # return db.list_collection_names()
            collection_names = db.list_collection_names()
            sorted_collection_names = sorted(collection_names)
            return sorted_collection_names
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
def fetch_table_attributes(conn, table_name, platform_id):
    attributes = []

    try:
        if platform_id == 1:  # PostgreSQL
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
                        WHERE conrelid = cl.oid AND conkey = ARRAY[a.attnum] AND contype = 'f'
                    ) AS is_foreign_key
                FROM information_schema.columns AS c
                JOIN pg_class AS cl ON cl.relname = c.table_name AND cl.relkind = 'r'
                JOIN pg_namespace AS n ON cl.relnamespace = n.oid AND n.nspname = c.table_schema
                LEFT JOIN pg_attribute AS a ON a.attrelid = cl.oid AND a.attname = c.column_name
                WHERE c.table_name = %s AND c.table_schema = 'public';
            """
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (table_name,))
                attributes = cursor.fetchall()

        elif platform_id == 2:  # MySQL
            query = """
                SELECT
                    c.COLUMN_NAME AS column_name,
                    c.DATA_TYPE AS data_type,
                    (EXISTS (
                        SELECT 1
                        FROM information_schema.STATISTICS
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = 'PRIMARY' AND COLUMN_NAME = c.COLUMN_NAME
                    )) AS is_primary_key,
                    (EXISTS (
                        SELECT 1
                        FROM information_schema.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = c.COLUMN_NAME AND CONSTRAINT_NAME != 'PRIMARY'
                    )) AS is_foreign_key
                FROM information_schema.COLUMNS AS c
                WHERE c.TABLE_NAME = %s;
            """
            with conn.cursor() as cursor:
                cursor.execute(query, (table_name, table_name, table_name))
                attributes = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

        elif platform_id == 3:  # MongoDB
            # สำหรับการดึงข้อมูลของ MongoDB ให้ใช้ข้อมูลจาก `conn` ซึ่งเป็น database
            # ดึงข้อมูลจาก `table_name` ซึ่งเป็นชื่อของ collection ใน MongoDB
            collection = conn[table_name]  # เชื่อมต่อกับ collection
            # ดึงข้อมูลของแต่ละฟิลด์ใน collection ด้วย `.find_one()`
            # ปรับปรุงโค้ดด้านล่างนี้ตามต้องการเพื่อให้ข้อมูลของ attributes เหมาะสมกับการใช้งาน
            sample_document = collection.find_one()
            
            # ดึง keys จาก `sample_document` เป็นชื่อของ attributes
            # คุณสามารถปรับโค้ดนี้ตามรูปแบบของข้อมูลที่คุณต้องการ
            if sample_document:
                for key, value in sample_document.items():
                    # คุณสามารถตรวจสอบประเภทของ `value` ได้จาก type() หรืออื่นๆ ตามต้องการ
                    data_type = type(value).__name__
                    
                    # สร้าง dictionary สำหรับ attribute และ append ไปยัง `attributes`
                    attributes.append({
                        'column_name': key,
                        'data_type': data_type,
                        'is_primary_key': False,  # MongoDB ไม่มี primary key โดยตรง แต่มี _id
                        'is_foreign_key': False   # ไม่มี foreign key โดยตรงใน MongoDB
                    })

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
                        # 'description': '',
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

def fetch_description(table_name, attr_id):
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        
        descriptions = []

        for id in attr_id:
            query = f"""
                    SELECT description FROM asset_attributes WHERE attribute_id = {id};
                """
        
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                description = cursor.fetchone()
                if description:
                    descriptions.append(description['description'])
    
    except Exception as e:
        print(f"Error fetching attributes for table {table_name}: {e}")
        descriptions = []

    finally:
        if conn:
            conn.close()

    return descriptions
