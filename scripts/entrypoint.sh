#!/usr/bin/env bash
set -e

echo "🚀 Starting Django container..."

# -----------------------------
# Wait for PostgreSQL
# -----------------------------
if [ "$DATABASE_HOSTNAME" ]; then
  echo "⏳ Waiting for PostgreSQL at $DATABASE_HOSTNAME:$DATABASE_PORT..."
  until nc -z "$DATABASE_HOSTNAME" "$DATABASE_PORT"; do
    sleep 1
  done
  echo "✅ PostgreSQL is available"
fi

# -----------------------------
# Migrations
# -----------------------------
echo "📦 Applying migrations..."
python manage.py migrate --noinput

# -----------------------------
# Collect static (prod only)
# -----------------------------
if [ "$DJANGO_ENV" = "production" ]; then
  echo "🎨 Collecting static files..."
  python manage.py collectstatic --noinput
fi

if [ -f /app/backend/Makefile ]; then
    make init
fi


# -----------------------------
# Start server
# -----------------------------
echo "🚀 Launching server..."
exec "$@"
