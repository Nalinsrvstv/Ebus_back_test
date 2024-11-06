# Use an official Python runtime as a parent image
FROM python:3.9.6

# Set environment variables for Python to run in unbuffered mode
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
#RUN pip install -r requirements.txt
# Set up a virtual environment and install Python dependencies
RUN python3 -m venv backendvenv
#RUN /bin/bash -c "source backendvenv/bin/activate && pip install -r requirements.txt"

# Set environment variables for Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=Ebus_backend.settings_dev

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run your application
CMD /bin/bash -c "source backendvenv/bin/activate && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    #echo \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass') if not User.objects.filter(username='admin').exists() else None\" | python manage.py shell && \
    python manage.py runserver 0.0.0.0:8000"
