from django.template import Library

from django.core.urlresolvers import reverse_lazy

register = Library()


@register.simple_tag(takes_context=True)
def thumbnail(context, source, size=None, method="crop"):
    if source and size:
        return reverse_lazy("proxy_image_full", args=[source, size, method])
    elif source:
        return reverse_lazy("proxy_image", args=[source])
    return None
