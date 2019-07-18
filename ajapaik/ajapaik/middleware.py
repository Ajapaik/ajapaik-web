from django.utils.deprecation import MiddlewareMixin
from subdomains.middleware import SubdomainURLRoutingMiddleware


class SubdomainMiddleware(MiddlewareMixin, SubdomainURLRoutingMiddleware):
    pass
