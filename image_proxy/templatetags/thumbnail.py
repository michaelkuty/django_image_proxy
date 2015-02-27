from django.template import Library

from django.conf import settings
from urlparse import urljoin
from django.core.urlresolvers import reverse_lazy

register = Library()

@register.simple_tag(takes_context=True)
def thumbnail(context, source, size="100x100", method="crop"):
    if source:
        return reverse_lazy("proxy_image_full", args=[source, size, method])
    return None