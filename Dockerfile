# ─────────────────────────────────────────────────────────────────────────────
# EduPredict — Multi-Stage Dockerfile
# Build: docker compose build
# Run:   docker compose up -d
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Production ─────────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Labels for image metadata
LABEL maintainer="EduPredict Team" \
      description="Student Performance Prediction — Django + ML" \
      version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=student_prediction.settings

WORKDIR /app

# Install only runtime system dependencies (no compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy project source
COPY . .

# Collect static files (requires SECRET_KEY to be set at build time)
ARG SECRET_KEY=build-time-placeholder-key
ARG DEBUG=False
ARG ALLOWED_HOSTS=localhost
RUN python manage.py collectstatic --noinput

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check: hit the liveness endpoint every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use the entrypoint script (runs migrations, then starts Gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]
