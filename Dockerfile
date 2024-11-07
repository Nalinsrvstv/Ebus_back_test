# Use the official Python 3.12 image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Specify the command to run the backend server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
