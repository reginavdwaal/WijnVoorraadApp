"""Production settings file"""

# pylint: disable=unused-wildcard-import,wildcard-import

import os
from decouple import config
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "vdwaal.net",
    "vino.vdwaal.net",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "oudwijndb": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "vdwanet_defaultdb",
        "USER": "vdwanet_django",
        "PASSWORD": DB_PASSWORD,
        "HOST": "127.0.0.1",
        "PORT": "3306",
    },
}

WWW_DIR = os.path.join(Path(BASE_DIR).resolve(), "public_html")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = os.path.join(WWW_DIR, "static")
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(WWW_DIR, "media")
