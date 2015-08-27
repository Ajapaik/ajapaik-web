from django.template import Library, Node, resolve_variable

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


@register.filter
def get_item(container, key):
    if type(container) is dict:
        return container.get(key)
    elif type(container) in (list, tuple):
        return container[key] if len(container) > key else None
    return None
