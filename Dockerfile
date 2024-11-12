# Use the official Python 3.10 image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

ENV DJANGO_SETTINGS_MODULE=busSchedulingServer.settings_dev

EXPOSE 8000

CMD ["python", "manage.py", "makemigrations"]

CMD ["python", "manage.py", "migrate"]
# Specify the command to run the backend server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
