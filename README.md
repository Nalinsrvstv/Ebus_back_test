# ebustoolserver

## Setup Instructions

### prerequisite
install python \
install PostgreSQL \
install git \
install your favorite IDE

### backend setup
git clone https://github.com/brsekhar/Ebus_backend.git \
git checkout project_creation_workflow \
git pull

-- install virtualenv \
pip install virtualenv 

-- create a virtual environment named 'backendvenv' \
python -m venv backendvenv

-- activate the virtual environment (on Windows) \
backendvenv\Scripts\activate

-- activate the virtual environment (on Unix or MacOS) \
source backendvenv/bin/activate

-- install dependencies from requirements.txt \
pip install -r requirements.txt

pip install setuptools \
pip install jsonschema

Go to busSchedulingServer/settings.py and change username and password 
~~~
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',      # Replace with your database name
        'USER': '<username>',  # Replace with your database user
        'PASSWORD': '<password>',  # Replace with your database password
        'HOST': 'localhost',       # Replace with your database host if necessary
        'PORT': '5432', 
    }
}
~~~
----------------run the following commands----------------------- \
-- create new database migration files based on changes made to your Django models \
python manage.py makemigrations

-- this command applies the database migrations, updating the actual database \
python manage.py migrate

-- create superuser \
python manage.py createsuperuser


----------------frequently used commands---------------------------- \
-- activate the virtual environment (on Windows) \
.\backendvenv\Scripts\activate

-- following command changes the execution policy for the current process to 'Bypass', allowing the execution of scripts without any restrictions \
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 

-- this command starts the Django development server \
python manage.py runserver

-- create database, user and assign all privileges
~~~
CREATE DATABASE ebus;
CREATE USER <username> WITH ENCRYPTED PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE ebus TO <username>;
~~~

In Postgres go to Login/Group Roles > select the user that you just created > properties > Privilages and check all the options > click Save