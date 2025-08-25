"""
WSGI config for aggregator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as e:
    print("Migration error:", e)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aggregator.settings')

application = get_wsgi_application()
