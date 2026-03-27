#!/usr/bin/env bash
# Render build script — install deps + run migrations + seed
set -o errexit

pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed (idempotent — skips existing records)
python seed.py
