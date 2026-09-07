# config/wsgi.py
#
# WSGI entry point. This is what gunicorn serves inside the Linux container (D-008),
# which is why gunicorn carries a sys_platform marker in requirements.txt - it is
# never installed or run on this Windows machine.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
