from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def ajapaik_ordering_link(album, order1, order2):
    if not order2:
        order2 = 'geotags'
    if album:
        url = reverse('project.home.views.frontpage', args=(album.id, 1))
    else:
        url = reverse('project.home.views.frontpage', args=(1,))
    if order1 and order2:
        url += '?order1=%s&order2=%s' % (order1, order2)
    elif order1:
        url += '?order1=%s' % order1
    elif order2:
        url += '?order2=%s' % order2
    return url