# Use an official Python runtime as a parent image
FROM python:3.11-slim

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
# This should match your Procfile but specifies a fixed port
# Fly.io injects $PORT, but standard Docker practice is to expose/use a fixed port internally
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]