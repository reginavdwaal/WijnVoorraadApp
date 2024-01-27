"""Custom filters for wijnvoorraad app"""

import os
from django import template
from django.conf import settings as conf_settings


register = template.Library()


@register.filter(is_safe=False)
def sub(value, arg):
    """Subtract the arg to the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ""


@register.filter
def env(key):
    """Get environment key"""
    return os.environ.get(key, None)


@register.filter
def setting(key):
    """Get setting based on key"""

    return getattr(conf_settings, key, None)
