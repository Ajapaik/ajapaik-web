from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('views',
	(r'^grappelli/', include('grappelli.urls')),
	(r'^admin/filebrowser/', include('filebrowser.urls')),
	(r'^admin/', include(admin.site.urls)),

	(r'^logout/', 'logout'),
	(r'^stream/', 'fetch_stream'),
	(r'^geotag/add/', 'geotag_add'),
	(r'^ajapaikaja/$', 'thegame'),
	(r'^kaart/$', 'mapview'),
	(r'^leaderboard/$', 'leaderboard'),
	(r'^top50/$', 'top50'),

	(r'^foto/(?P<photo_id>\d+)/$', 'photo'),
	(r'^foto/(?P<slug>[\w\_\-]+)/$', 'photoview'),
	(r'^foto_url/(?P<photo_id>\d+)/$', 'photo_url'),
	(r'^foto_thumb/(?P<photo_id>\d+)/$', 'photo_thumb'),
	(r'^foto/(?P<photo_id>\d+)/upload/$', 'photo_upload'),
	
	(r'^$', 'frontpage')
) + patterns('',
	(r'^facebook/(?P<stage>[a-z_]+)/', 'facebook.facebook_handler'),
	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs','packages': ('project')}),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
	)
