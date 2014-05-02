from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
admin.autodiscover()

urlpatterns = patterns('views',
	#(r'^grappelli/', include('grappelli.urls')),
	(r'^admin/filebrowser/', include('filebrowser.urls')),
	(r'^admin/', include(admin.site.urls)),

	(r'^logout/', 'logout'),
	(r'^stream/', 'fetch_stream'),
	(r'^geotag/add/', 'geotag_add'),
	(r'^ajapaikaja/$', 'thegame'),
	(r'^kaart/$', 'mapview'),
	(r'^leaderboard/$', 'leaderboard'),
	(r'^top50/$', 'top50'),
	(r'^heatmap/$', 'heatmap'),
	(r'^heatmap/(?P<photo_id>\d+)/$', 'photo_heatmap'),
	(r'^heatmap/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug_heatmap'),

	(r'^foto/(?P<photo_id>\d+)/upload/$', 'photo_upload'),
	(r'^foto/(?P<photo_id>\d+)/$', 'photo'),
	(r'^foto/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
	(r'^foto_large/(?P<photo_id>\d+)/$', 'photo_large'),
	(r'^foto_url/(?P<photo_id>\d+)/$', 'photo_url'),
	(r'^foto_thumb/(?P<photo_id>\d+)/$', 'photo_thumb'),

	(r'^$', 'frontpage')
) + patterns('',
	(r'^facebook/(?P<stage>[a-z_]+)/', 'facebook.facebook_handler'),
	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs','packages': ('project')}),
	(r'^favicon\.ico$', RedirectView.as_view(url='/media/gfx/favicon.ico')),
	(r'^feed/photos/', RedirectView.as_view(url='http://api.ajapaik.ee/?action=photo&format=atom')),
)

# not sure how to distinguish between LIVE and DEV other than GA code
if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
	urlpatterns += patterns('',
		(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
	)
else:
	urlpatterns += patterns('',
		(r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')),
	)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
	)

if 'rosetta' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
	url(r'^rosetta/', include('rosetta.urls')),
	)

