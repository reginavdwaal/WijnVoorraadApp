"""Production settings file"""
# pylint: disable=unused-wildcard-import,wildcard-import
from decouple import config
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "vdwaal.net",
    "fly.vdwaal.net",
]

WWW_DIR = Path(BASE_DIR).resolve().parent / "public_html/xxxxxx/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = WWW_DIR / "static/"
STATIC_URL = "static/"
