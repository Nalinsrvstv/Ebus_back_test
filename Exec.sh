#!/bin/bash

# Activate the virtual environment
source backendvenv/bin/activate

# Install requirements
pip install -r requirements.txt

# Make migrations and migrate the database
python manage.py makemigrations
python manage.py migrate

# Uncomment the following line if you want to create a superuser
# echo "your_superuser_password" | python manage.py createsuperuser --noinput --username your_username

# Run the server
python manage.py runserver 0.0.0.0:8000
