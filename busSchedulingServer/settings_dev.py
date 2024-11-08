from .settings import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# local setup
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_3",#"ebus",  # Replace with your database name
        "USER": "user2",#"rohit",  # Replace with your database user
        "PASSWORD": "0901",#"rohit",  # Replace with your database password
        "HOST": "13.126.80.198",  # Replace with your database host if necessary
        "PORT": "5432",
    }
}
