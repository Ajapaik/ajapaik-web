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
    (r'^thegame/$', 'thegame'),
    (r'^photo/(?P<photo_id>\d+)/$', 'photo'),
    (r'^map/$', 'mapview'),
    
    (r'^$', 'frontpage')
) + patterns('',
    (r'^facebook/(?P<stage>[a-z_]+)/', 'facebook.facebook_handler'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
