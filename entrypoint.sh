#!/bin/sh
set -e

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Collect static files..."
python manage.py collectstatic --noinput

echo "Apply migrations..."
python manage.py migrate --noinput

exec "$@"
