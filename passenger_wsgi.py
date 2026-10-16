"""passenger file to connect django app to server environment"""
import os
import sys

# Must be set before WijnProject.wsgi is imported: it only defines `app` for
# non-dev settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WijnProject.settings.prod")

from WijnProject.wsgi import app  # pylint: disable=wrong-import-position

sys.path.insert(0, os.path.dirname(__file__))

application = app
