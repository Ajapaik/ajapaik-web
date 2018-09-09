from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import MediaWikiProvider


urlpatterns = default_urlpatterns(MediaWikiProvider)
