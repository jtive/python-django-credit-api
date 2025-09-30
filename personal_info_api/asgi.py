"""
ASGI config for personal_info_api project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_info_api.settings')

application = get_asgi_application()
