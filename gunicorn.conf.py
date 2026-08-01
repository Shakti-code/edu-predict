# ─────────────────────────────────────────────────────────────────────────────
# EduPredict — Gunicorn Production Configuration
#
# Usage:
#   gunicorn -c gunicorn.conf.py student_prediction.wsgi:application
# ─────────────────────────────────────────────────────────────────────────────

import multiprocessing
import os

# ── Server Socket ─────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# ── Worker Processes ──────────────────────────────────────────────────────────
# Recommended: 2 × CPU cores + 1
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
graceful_timeout = 30
keepalive = 5

# ── Worker Recycling ──────────────────────────────────────────────────────────
# Restart workers after handling this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# ── Preloading ────────────────────────────────────────────────────────────────
# Load application code before worker processes are forked
# Saves RAM via copy-on-write but means code changes require full restart
preload_app = True

# ── Logging ───────────────────────────────────────────────────────────────────
accesslog = '-'   # stdout
errorlog = '-'    # stderr
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sμs'

# ── Process Naming ────────────────────────────────────────────────────────────
proc_name = 'edupredict'

# ── Server Mechanics ──────────────────────────────────────────────────────────
# Detach from controlling terminal (False when running in Docker)
daemon = False
tmp_upload_dir = None

# ── Security ──────────────────────────────────────────────────────────────────
# Limit the size of HTTP request headers (default 8190)
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
