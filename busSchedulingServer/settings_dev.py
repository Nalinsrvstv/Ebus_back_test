from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ebus",  # Replace with your database name
        "USER": "rohit",  # Replace with your database user
        "PASSWORD": "rohit",  # Replace with your database password
        "HOST": "localhost",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
