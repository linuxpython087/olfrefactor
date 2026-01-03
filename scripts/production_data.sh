#!/usr/bin/env bash
set -e
echo "📁 Creating logs directory..."
mkdir -p /app/logs
chmod -R 755 /app/logs

echo "🚀 Running production data bootstrap..."

# Wait for DB
if [ "$DATABASE_HOSTNAME" ]; then
  echo "⏳ Waiting for DB..."
  until nc -z "$DATABASE_HOSTNAME" "$DATABASE_PORT"; do
    sleep 1
  done
fi

echo "📦 Applying migrations (safety)..."
cd backend && python manage.py migrate --noinput

echo "👤 Seeding roles..."
 python manage.py seed_role

echo "📊 Importing SVU indicators..."

echo "✅ Production data bootstrap completed."
