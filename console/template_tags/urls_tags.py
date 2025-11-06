from django import template
from django.conf import settings

register = template.Library()

@register.filter
def absolute_url(value, request):
    """Converts a relative URL to an absolute URL using the request object."""
    if value and request:
        return request.build_absolute_uri(value)
    return value