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

echo "Loading fixtures..."

# Load FAQ fixtures
FAQ_COUNT=$(python manage.py shell -c "from faq.models import Kerdes; print(Kerdes.objects.count())" 2>/dev/null | tail -1 | tr -d '\r\n' || echo "0")
if [ "$FAQ_COUNT" -eq "0" ]; then
    python manage.py loaddata faq_data
    echo "✅ FAQ fixtures loaded successfully!"
else
    echo "ℹ️  FAQ fixtures already exist ($FAQ_COUNT entries), skipping..."
fi

# Load Szabalyzat fixtures
SZABALYZAT_COUNT=$(python manage.py shell -c "from szabalyzat.models import Szabalyzat; print(Szabalyzat.objects.count())" 2>/dev/null | tail -1 | tr -d '\r\n' || echo "0")
if [ "$SZABALYZAT_COUNT" -eq "0" ]; then
    python manage.py loaddata szabalyzat_data
    echo "✅ Szabalyzat fixtures loaded successfully!"
else
    echo "ℹ️  Szabalyzat fixtures already exist ($SZABALYZAT_COUNT entries), skipping..."
fi

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000