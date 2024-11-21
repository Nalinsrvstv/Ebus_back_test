from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ebus",#"test_2",  # Replace with your database name
        "USER": "rohit",#"nalin",  # Replace with your database user
        "PASSWORD": "rohit",#"2209"  # Replace with your database password
        "HOST": "127.0.0.1",#"13.201.75.227",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
