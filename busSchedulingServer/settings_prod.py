from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# ec2 prod setup
# don't change these settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",  # Replace with your database name
        "USER": "root",  # Replace with your database user
        "PASSWORD": "root@#23",  # Replace with your database password
        "HOST": "localhost",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
