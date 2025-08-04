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

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000