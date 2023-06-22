from django import template
from django.template.defaultfilters import floatformat
from django.templatetags.tz import localtime

register = template.Library()

@register.filter
def localize(value, arg=None):
    return localtime(value, arg)

@register.filter
def format_float(value, arg=None):
    return floatformat(value, arg)
