#!/bin/sh
set -e

# Исправить права на volume (контейнер запускается от root)
chown -R appuser:appuser /app/data

echo "Running database migrations..."
su appuser -c "alembic upgrade head"

echo "Seeding admin user..."
su appuser -c "python -m app.seed_admin"

echo "Starting application..."
exec su -p appuser -c "exec uvicorn app.main:app --host 0.0.0.0 --port 8000"
