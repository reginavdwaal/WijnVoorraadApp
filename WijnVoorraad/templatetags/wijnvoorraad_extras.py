"""Custom filters for wijnvoorraad app"""

import os
from django.conf import settings as conf_settings
from django import template
from WijnVoorraad import wijnvars

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

@register.filter(name='range')
def filter_range(start, end):
    return range(start, end+1)

@register.filter(is_safe=False)
def kolomnr(recordnr, aantal_kolommen):
    """Bereken het kolomnummer gebaseerd op recordnummer en aantal kolommen"""
    try:
        return int(recordnr) % int(aantal_kolommen)
    except (ValueError, TypeError):
        return ""

@register.filter(is_safe=False)
def wijnsoort_to_css(wijnsoort):
    css = wijnvars.unified_wijnsoort(wijnsoort)
    return css

@register.filter
def env(key):
    """Get environment key"""
    return os.environ.get(key, None)


@register.filter
def setting(key):
    """Get setting based on key"""

    return getattr(conf_settings, key, None)
