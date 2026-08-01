"""
Health check endpoints for production monitoring.

/health/       — Lightweight liveness check (always returns 200 OK).
/health/ready/ — Readiness check (verifies DB connection + ML model loaded).
"""

import os
import logging

from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger('predictor')

# Path to the trained ML model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model.pkl')


def liveness(request):
    """
    Liveness probe — indicates the application process is running.
    Used by container orchestrators (Docker, Kubernetes) to detect crashed processes.
    """
    return JsonResponse({'status': 'healthy'}, status=200)


def readiness(request):
    """
    Readiness probe — indicates the application is ready to serve traffic.
    Checks:
      1. Database connectivity
      2. ML model file exists and is accessible
    """
    checks = {
        'status': 'healthy',
        'database': 'ok',
        'model': 'loaded',
    }
    status_code = 200

    # Check database connectivity
    try:
        connection.ensure_connection()
        if not connection.is_usable():
            raise Exception('Database connection is not usable')
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        checks['status'] = 'unhealthy'
        status_code = 503
        logger.error('Health check: database connectivity failed — %s', e)

    # Check ML model availability
    if not os.path.exists(MODEL_PATH):
        checks['model'] = 'missing'
        checks['status'] = 'unhealthy'
        status_code = 503
        logger.warning('Health check: ML model not found at %s', MODEL_PATH)

    return JsonResponse(checks, status=status_code)
