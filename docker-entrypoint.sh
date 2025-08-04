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

echo "Loading FAQ fixtures..."
# Check if FAQ fixtures are already loaded to avoid duplicates
FAQ_COUNT=$(python manage.py shell -c "from faq.models import Kerdes; print(Kerdes.objects.count())" 2>/dev/null | tail -1 | tr -d '\r\n' || echo "0")
if [ "$FAQ_COUNT" -eq "0" ]; then
    python manage.py loaddata faq_data
    echo "✅ FAQ fixtures loaded successfully!"
else
    echo "ℹ️  FAQ fixtures already exist ($FAQ_COUNT entries), skipping..."
fi

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000