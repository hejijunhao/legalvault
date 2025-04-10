# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This assumes your Dockerfile is in the backend directory
COPY . .

# Make port 8080 available to the world outside this container
# Fly.io will map this internal port to external ports 80/443
EXPOSE 8080

# Define the command to run your app using uvicorn
# Using shell form to ensure environment variable expansion
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}