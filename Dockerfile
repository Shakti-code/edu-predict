# ─────────────────────────────────────────────────────────────────────────────
# EduPredict — Dockerfile
# Build: docker build -t edupredict .
# Run:   docker run -p 8000:8000 --env-file .env edupredict
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (needed for psycopg2, numpy, scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Collect static files (requires SECRET_KEY to be set at build time or as ARG)
ARG SECRET_KEY=build-time-placeholder-key
ARG DEBUG=False
ARG ALLOWED_HOSTS=localhost
RUN python manage.py collectstatic --noinput

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start gunicorn
CMD gunicorn student_prediction.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-file - \
    --access-logfile -
