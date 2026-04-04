<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    swig \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install old setuptools for pyafipws 2to3 translation
RUN pip install "setuptools<58.0.0" wheel "urllib3<2" "cryptography<41"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose port and run
EXPOSE 8080
=======
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create static directory if it doesn't exist (though we should move to Cloud Storage)
RUN mkdir -p static

# Expose the port the app runs on
EXPOSE 8000

# Run uvicorn
>>>>>>> financial-project/main
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
