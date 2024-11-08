from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "your_database_name;",#"ebus",  # Replace with your database name
        "USER": "user_nalin",#"rohit",  # Replace with your database user
        "PASSWORD": "2209",#"rohit",  # Replace with your database password
        "HOST": "3.111.40.37",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
