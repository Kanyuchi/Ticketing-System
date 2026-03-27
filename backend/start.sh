#!/usr/bin/env bash
set -e

echo "=== Starting Proof of Talk Ticketing API ==="

# Run migrations (safe to re-run — alembic tracks what's applied)
echo "Running database migrations..."
alembic upgrade head || echo "WARNING: migrations failed (may already be applied)"

# Seed data (idempotent — skips existing records)
echo "Seeding database..."
python seed.py || echo "WARNING: seed failed (data may already exist)"

# Start the server
echo "Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
