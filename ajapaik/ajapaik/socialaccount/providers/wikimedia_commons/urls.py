from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import WikimediaCommonsProvider

urlpatterns = default_urlpatterns(WikimediaCommonsProvider)
