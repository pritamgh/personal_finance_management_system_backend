#!/bin/sh

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z "$POSTGRESQLDB_HOST" "$POSTGRESQLDB_PORT"; do
  sleep 1
done

echo "✅ Postgres is up. Applying migrations..."
alembic upgrade head

echo "🚀 Starting FastAPI app..."
exec python main.py
