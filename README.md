# Almonds
### This repository is used for the Senior Project named Almonds.
Almonds is a database hub used by organizations to generate metadata following the DGA metadata format, making the organization's database more explorable.

## Install package components
This is for command prompt or terminal
### Back-end:
_**Navigate to backend folder first_
```
$ cd backend
```
```
$ pip install -r requirements.txt
```
### Front-end:
_**Navigate to frontend folder first_
```
$ cd frontend
```
```
$ npm install axios react-router-dom jwt-decode
```

## Enviroment setup


## Database setup
### Example for PostgreSQL:
_backend/backend/settings.py_
``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Migrate the models (database tables) from Django to PostgreSQL (database).
In Django, you can write a model file to define database tables and use commands to create those tables in the database.
### The command to migrate Django models to the database:
_**Don't forget to navigate to backend folder_
```
$ python manage.py makemigrations
$ python manage.py migrate
```
## Features checklists
Feature | Description | |
-----|-----|-----|
Database Connection|Adding support for more database platforms. Previously, only PostgreSQL was supported; now, we are adding MySQL and MongoDB.|**DONE**
Data Catalog|Lists all database connection details for better exploration.|**DONE**
Data Overview|Lists each database's information and all tables within the database.|**DONE**
Metadata|Displays metadata with a description field for each attribute to provide details.|**DONE**
Generate ER-Diagram|Generate an ER-diagram to show the relationships between data.|_NOT DONE_
