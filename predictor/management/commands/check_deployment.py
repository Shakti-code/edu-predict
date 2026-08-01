"""
Custom management command to verify the deployment environment is correctly configured.

Usage:
    python manage.py check_deployment

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

import os
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Verify that the deployment environment is correctly configured for production.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n═══ EduPredict Deployment Check ═══\n'))

        checks = [
            ('SECRET_KEY is not default', self._check_secret_key),
            ('DEBUG is False', self._check_debug),
            ('Database connectivity', self._check_database),
            ('ML model file exists', self._check_model),
            ('Static files directory exists', self._check_static),
            ('ALLOWED_HOSTS is configured', self._check_allowed_hosts),
        ]

        passed = 0
        failed = 0

        for name, check_fn in checks:
            try:
                ok, detail = check_fn()
                if ok:
                    self.stdout.write(f'  ✓ {name} — {detail}')
                    passed += 1
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ {name} — {detail}'))
                    failed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ {name} — Exception: {e}'))
                failed += 1

        self.stdout.write('')
        if failed == 0:
            self.stdout.write(self.style.SUCCESS(
                f'  All {passed} checks passed. Ready for deployment!\n'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'  {failed} check(s) failed, {passed} passed. Fix issues before deploying.\n'
            ))
            sys.exit(1)

    def _check_secret_key(self):
        key = settings.SECRET_KEY
        if 'insecure' in key or 'change-me' in key or key == 'your-very-secret-key-here':
            return False, 'Using default/insecure SECRET_KEY'
        return True, f'Custom key set ({len(key)} chars)'

    def _check_debug(self):
        if settings.DEBUG:
            return False, 'DEBUG is True — must be False in production'
        return True, 'DEBUG is False'

    def _check_database(self):
        try:
            connection.ensure_connection()
            db_engine = settings.DATABASES['default']['ENGINE']
            if 'sqlite' in db_engine:
                return False, f'Using SQLite ({db_engine}) — use PostgreSQL in production'
            return True, f'Connected to {db_engine}'
        except Exception as e:
            return False, f'Cannot connect: {e}'

    def _check_model(self):
        model_path = os.path.join(settings.BASE_DIR, 'model', 'model.pkl')
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            return True, f'Found ({size_mb:.1f} MB)'
        return False, 'model/model.pkl not found'

    def _check_static(self):
        static_root = settings.STATIC_ROOT
        if static_root and os.path.isdir(static_root):
            file_count = sum(len(files) for _, _, files in os.walk(static_root))
            return True, f'{file_count} files in {static_root}'
        return False, f'STATIC_ROOT ({static_root}) does not exist — run collectstatic'

    def _check_allowed_hosts(self):
        hosts = settings.ALLOWED_HOSTS
        if not hosts or hosts == ['*']:
            return False, 'ALLOWED_HOSTS is empty or wildcard (*)'
        return True, f'Configured: {", ".join(hosts)}'
