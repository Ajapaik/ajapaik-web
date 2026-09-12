from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme


class safeUrlAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        return url_has_allowed_host_and_scheme(url, allowed_hosts=settings.ALLOWED_HOSTS)
