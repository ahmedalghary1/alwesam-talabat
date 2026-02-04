#!/bin/bash

# Exit on error
set -e

echo "ðŸ³ Starting Alwesam-Talabat Django Application..."
echo "=================================================="

# Wait for PostgreSQL to be ready
echo "â³ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "âœ… PostgreSQL is ready!"

# Wait for Redis to be ready
echo "â³ Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "âœ… Redis is ready!"

# Run migrations
echo "ðŸ”„ Running database migrations..."
python manage.py migrate --noinput
echo "âœ… Migrations completed!"

# Collect static files
echo "ðŸ“¦ Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "âœ… Static files collected!"

# Create superuser if it doesn't exist (using improved script)
echo "ðŸ‘¤ Checking for superuser..."
python create_superuser.py || echo "âš ï¸  Superuser creation skipped (not critical)"

echo "=================================================="
echo "ðŸš€ Starting Django development server..."
echo "ðŸ“ Server will be available at: http://localhost:8000"
echo "ðŸ“ Admin panel: http://localhost:8000/admin/"
echo "ðŸ“ API docs: http://localhost:8000/api/docs/"
echo "=================================================="


# Start server
exec "$@"


