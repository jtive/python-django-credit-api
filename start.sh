#!/bin/bash

# Startup script for Django Personal Info API

echo "Starting Django Personal Info API..."

# Wait for database to be ready
echo "Waiting for database connection..."
python manage.py shell -c "
import time
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        print('Database connection successful!')
        break
    except Exception as e:
        retry_count += 1
        print(f'Database connection attempt {retry_count} failed: {e}')
        if retry_count >= max_retries:
            print('Max database connection retries reached. Exiting.')
            exit(1)
        time.sleep(2)
"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 personal_info_api.wsgi:application
