# Use Python 3.11 alpine image as base
FROM python:3.11-alpine

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    curl

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create messages directory and ensure proper permissions
RUN mkdir -p services/message_factory/messages \
    && chown -R nobody:nogroup /app

# Switch to non-root user
USER nobody

# Command to run the application
CMD ["python", "main.py"]