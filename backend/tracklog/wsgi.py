"""
WSGI config for tracklog project.
"""
import os
import sys

# Ensure backend package root is on path (required for Vercel serverless).
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracklog.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
