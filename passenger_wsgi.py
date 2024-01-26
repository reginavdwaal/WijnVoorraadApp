"""passenger file to connect django app to server environment"""
import os
import sys

from WijnProject.wsgi import app

sys.path.insert(0, os.path.dirname(__file__))

environ = os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "WijnProject.settings.dev"
)

application = app
