from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# ec2 prod setup
# don't change these settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_2",#"postgres",  # Replace with your database name
        "USER": "nalin",#"root",  # Replace with your database user
        "PASSWORD": "2209",#"root@#23",  # Replace with your database password
        "HOST": "13.201.75.227",#"localhost",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
