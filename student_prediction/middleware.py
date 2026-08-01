"""
Production middleware for EduPredict.

RequestIDMiddleware  — Attaches a unique UUID to each request for log correlation.
RequestLoggingMiddleware — Logs method, path, status code, and duration for each request.
"""

import logging
import time
import uuid

logger = logging.getLogger('django.request')


class RequestIDMiddleware:
    """
    Attach a unique request ID to every incoming request.
    This ID is forwarded in the 'X-Request-ID' response header and can be
    used to correlate logs across services.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use an incoming X-Request-ID header if present (from reverse proxy),
        # otherwise generate a new one
        request_id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        request.request_id = request_id

        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response


class RequestLoggingMiddleware:
    """
    Log the HTTP method, path, response status code, and duration (ms)
    for every request. Skips health check endpoints to avoid log noise.
    """

    SKIP_PATHS = {'/health/', '/health/ready/'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for health check endpoints
        if request.path in self.SKIP_PATHS:
            return self.get_response(request)

        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        request_id = getattr(request, 'request_id', '-')
        logger.info(
            '%s %s %s %.1fms [%s]',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
