#!/bin/bash

# Exit on error
set -e

echo "🐳 Starting Alwesam-Talabat Django Application..."
echo "=================================================="

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed!"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected!"

# Create superuser if it doesn't exist (using improved script)
echo "👤 Checking for superuser..."
python create_superuser.py || echo "⚠️  Superuser creation skipped (not critical)"

echo "=================================================="
echo "🚀 Starting Django development server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📍 Admin panel: http://localhost:8000/admin/"
echo "📍 API docs: http://localhost:8000/api/docs/"
echo "=================================================="


# Start server
exec "$@"
