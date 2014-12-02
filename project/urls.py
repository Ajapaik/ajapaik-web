from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers
from project.home.photo_import import PhotoViewSet, CityViewSet, SourceViewSet

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'api/photos', PhotoViewSet)
router.register(r'api/cities', CityViewSet)
router.register(r'api/sources', SourceViewSet)

urlpatterns = patterns('project.home.views',
	url(r'^logout/', 'logout'),
	url(r'^stream/', 'fetch_stream'),
	url(r'^difficulty_feedback/', 'difficulty_feedback'),
	url(r'^log_user_map_action/', 'log_user_map_action'),
	url(r'^geotag/add/', 'geotag_add'),
	url(r'^ajapaikaja/$', 'thegame'),
	url(r'^kaart/$', 'mapview'),
	url(r'^leaderboard/$', 'leaderboard'),
	url(r'^top50/$', 'top50'),
	url(r'^rephoto_top50/$', 'rephoto_top50'),
	url(r'^heatmap/$', 'heatmap'),
	url(r'^heatmap/(?P<photo_id>\d+)/$', 'photo_heatmap'),
	url(r'^heatmap/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug_heatmap'),
	url(r'^foto/(?P<photo_id>\d+)/upload/$', 'photo_upload'),
	url(r'^foto/(?P<photo_id>\d+)/$', 'photo'),
	url(r'^foto/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
	url(r'^foto_large/(?P<photo_id>\d+)/$', 'photo_large'),
	url(r'^foto_url/(?P<photo_id>\d+)/$', 'photo_url'),
	url(r'^foto_thumb/(?P<photo_id>\d+)/$', 'photo_thumb'),
	url(r'^foto_thumb/(?P<photo_id>\d+)/(?P<thumb_size>.*)/', 'photo_thumb'),
    url(r'^grid/(?P<city_id>\d+)/$', 'grid'),
    url(r'^grid_infinity/(?P<city_id>\d+)/(?P<end>\d+)/$', 'grid_infinite_scroll'),
	url(r'^public_photo_upload/$', 'public_photo_upload'),
	url(r'^public_photo_upload_handler/$', 'public_photo_upload_handler'),
    url(r'^csv_upload/$', 'csv_upload'),
	url(r'^europeana/$', 'europeana'),
    url(r'^pane_contents/$', 'pane_contents'),
	url(r'^$', 'frontpage')
)

urlpatterns += patterns('',
   url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^admin_tools/', include('admin_tools.urls')),
   url(r'^facebook/(?P<stage>[a-z_]+)/', 'project.home.facebook.facebook_handler'),
   #url(r'^google_login', 'google_plus.google_login'),
   #url(r'^oauth2callback', 'google_plus.auth_return'),
   url(r'^i18n/', include('django.conf.urls.i18n')),
   url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs', 'packages': ('project')}),
   url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
   url(r'^feed/photos/', RedirectView.as_view(url='http://api.ajapaik.ee/?action=photo&format=atom')),
   url(r'^', include(router.urls)),
   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')))

handler500 = 'project.home.views.custom_500'
handler404 = 'project.home.views.custom_404'

if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
	urlpatterns += patterns('', (
	r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
	urlpatterns += patterns('', (
	r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
	urlpatterns += patterns('', (
	r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )