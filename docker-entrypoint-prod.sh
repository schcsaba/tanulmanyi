#!/bin/bash

# Exit on any error
set -e

echo "Waiting for MySQL to be ready..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

echo "Running database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
gunicorn tanulmanyi.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gthread \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile -