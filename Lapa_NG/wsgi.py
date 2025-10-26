"""
WSGI config for Lapa_NG project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lapa_NG.settings')

application = get_wsgi_application()

if os.environ.get("RUN_COLLECTSTATIC_ON_STARTUP") == "1":
    try:
        call_command("collectstatic", "--noinput", verbosity=0)
    except Exception:
        # swallow and log, so a failure doesn't break startup
        import logging
        logging.exception("collectstatic at startup failed")
