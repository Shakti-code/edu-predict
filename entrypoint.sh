#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# EduPredict — Docker Entrypoint Script
# Runs database migrations, collects static files, and starts Gunicorn.
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "──────────────────────────────────────"
echo "  EduPredict — Starting Application"
echo "──────────────────────────────────────"

# ── 1. Wait for Database ────────────────────────────────────────────────────
echo "[1/4] Waiting for database..."
python -c "
import time, os, sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_prediction.settings')
django.setup()
from django.db import connection
for i in range(30):
    try:
        connection.ensure_connection()
        print('Database is ready!')
        sys.exit(0)
    except Exception:
        print(f'Attempt {i+1}/30 — waiting for database...')
        time.sleep(2)
print('ERROR: Database not available after 60 seconds')
sys.exit(1)
"

# ── 2. Run Migrations ──────────────────────────────────────────────────────
echo "[2/4] Running database migrations..."
python manage.py migrate --noinput

# ── 3. Collect Static Files ────────────────────────────────────────────────
echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput

# ── 4. Create Superuser (if env variables are set) ─────────────────────────
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "[3.5/4] Creating superuser (if not exists)..."
    python manage.py createsuperuser \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@edupredict.com}" \
        --noinput 2>/dev/null || echo "Superuser already exists, skipping."
fi

# ── 5. Start Gunicorn ──────────────────────────────────────────────────────
echo "[4/4] Starting Gunicorn..."
echo "──────────────────────────────────────"
exec gunicorn \
    --config gunicorn.conf.py \
    student_prediction.wsgi:application
