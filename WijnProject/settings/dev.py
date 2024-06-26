"""Development settings file"""

# pylint: disable=unused-wildcard-import,wildcard-import
import os
from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-d)44)!fy0uooxhg5)ak2+d#5vt3e@ynoko_x*anr$!95c@p!a7"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["espresso", "localhost", "AsusRegina", "192.168.178.96"]

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
        "HOST": "87.236.102.45",
        "PORT": "3306",
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = "static/"
STATIC_ROOT = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
