from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_2",#"ebus",  # Replace with your database name
        "USER": "nalin",#"rohit",  # Replace with your database user
        "PASSWORD": "2209",#"rohit",  # Replace with your database password
        "HOST": "13.233.11.141",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
