from django.template import Library, Node, resolve_variable
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines

from django.conf import settings

register = Library()


class AddGetParameter(Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        req = resolve_variable('request', context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = value.resolve(context)
        return '?%s' % params.urlencode()


@register.tag
def add_get(parser, token):
    pairs = token.split_contents()[1:]
    values = {}
    for pair in pairs:
        s = pair.split('=', 1)
        values[s[0]] = parser.compile_filter(s[1])
    return AddGetParameter(values)


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, '')


@register.filter
def div(value, arg):
    try:
        value = int(value)
        arg = int(arg)
        if arg: return value / arg
    except:
        pass
    return ''


def remove_newlines(text):
    normalized_text = normalize_newlines(text)
    return mark_safe(normalized_text.replace('\n', ' '))


remove_newlines.is_safe = True
remove_newlines = stringfilter(remove_newlines)
register.filter(remove_newlines)
