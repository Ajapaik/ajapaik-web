from allauth.account.adapter import DefaultAccountAdapter
from django.utils.http import is_safe_url
from django.conf import settings

class safeUrlAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        return is_safe_url(url, allowed_hosts=settings.ALLOWED_HOSTS)
