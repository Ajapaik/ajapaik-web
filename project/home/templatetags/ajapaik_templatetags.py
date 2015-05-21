from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def ajapaik_ordering_link(album, order1, order2):
    if not order1:
        order1 = 'time'
    if not order2:
        order2 = 'geotags'
    if album:
        url = reverse('project.home.views.frontpage', args=(album.id, 1))
    else:
        url = reverse('project.home.views.frontpage', args=(1,))
    url += '?order1=%s&order2=%s' % (order1, order2)
    return url