# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies for testing
COPY requirements-mypy.txt /app/
RUN pip install --no-cache-dir -r requirements-mypy.txt

# Copy project
COPY . /app/

# Make startup script executable
RUN chmod +x /app/start.sh

# Run type checking during build (optional - can be disabled for faster builds)
RUN mypy --config-file mypy-basic.ini api/ || echo "Type checking completed with warnings"

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application using startup script
CMD ["/app/start.sh"]
