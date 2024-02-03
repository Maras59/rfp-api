# Use the official Python image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /rfp_api

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Specify the command to run your Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Build the Podman container image
# podman build -t django-app .

# Run the Podman container
# podman run -p 8000:8000 django-app