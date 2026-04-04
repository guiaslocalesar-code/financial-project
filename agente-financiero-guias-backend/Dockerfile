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
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
