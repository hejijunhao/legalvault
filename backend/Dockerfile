# Build Stage: Used to install dependencies and build the app
# We use python:3.11-alpine for a smaller base image (~50 MB vs. ~120 MB for slim)
FROM python:3.11-alpine AS builder

# Set the working directory inside the container to /app
WORKDIR /app

# Ensure Python output is unbuffered for better logging in containers
ENV PYTHONUNBUFFERED=1

# Install build-time system dependencies using Alpine's package manager (apk)
# --no-cache avoids storing package cache, keeping the image small
# gcc, musl-dev, python3-dev, libpq-dev are needed to compile some Python packages
RUN apk add --no-cache gcc musl-dev python3-dev libpq-dev

# Copy the requirements file first to leverage Docker layer caching
# If requirements.txt doesn't change, this layer won't rebuild
COPY requirements.txt .

# Install Python dependencies from requirements.txt
# --no-cache-dir ensures pip doesn't store cache files, reducing image size
RUN pip install --no-cache-dir -r requirements.txt

# Runtime Stage: The final image that runs the app
# We start fresh with python:3.11-alpine to keep the image minimal
FROM python:3.11-alpine

# Set the working directory for the runtime stage
WORKDIR /app

# Ensure Python output is unbuffered (same as build stage)
ENV PYTHONUNBUFFERED=1

# Set the default port for the app (Fly.io will map this to 80/443 externally)
ENV PORT=8080

# Install runtime system dependencies
# libpq is needed for PostgreSQL (used by psycopg/asyncpg for Supabase)
RUN apk add --no-cache libpq

# Copy the installed Python dependencies from the builder stage
# This excludes build-time dependencies (e.g., gcc) from the final image
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the rest of the application code into the container
# .dockerignore ensures we exclude unnecessary files (e.g., tests/, .git/)
COPY . .

# Expose port 8080 for the app (Fly.io maps this to external 80/443)
EXPOSE 8080

# Run the app using uvicorn in exec form (["command", "arg1", ...])
# Hardcode the port to avoid variable substitution issues
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]