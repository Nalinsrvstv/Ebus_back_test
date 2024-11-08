from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_4",#"ebus",  # Replace with your database name
        "USER": "user3",#"rohit",  # Replace with your database user
        "PASSWORD": "2209",#"rohit",  # Replace with your database password
        "HOST": "3.109.209.101",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
