#!/usr/bin/env bash
set -e

echo "🚀 Running production data bootstrap..."

# Wait for DB
if [ "$DATABASE_HOSTNAME" ]; then
  echo "⏳ Waiting for DB..."
  until nc -z "$DATABASE_HOSTNAME" "$DATABASE_PORT"; do
    sleep 1
  done
fi

echo "📦 Applying migrations (safety)..."
python manage.py migrate --noinput

echo "👤 Seeding roles..."
python manage.py seed_role

echo "📊 Importing SVU indicators..."

echo "✅ Production data bootstrap completed."
