from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

admin.autodiscover()

# TODO: Locale specific URLs
urlpatterns = patterns('project.sift.views',
   url(r'^logout/', 'logout'),
   url(r'^$', 'cat_results'),
   url(r'^about/$', 'cat_about'),
   url(r'^tag/$', 'cat_tagger'),
   url(r'^filter/$', 'cat_results'),
   url(r'^cat/v1/login/$', 'cat_login'),
   url(r'^cat/v1/logout/$', 'cat_logout'),
   url(r'^cat/v1/albums/$', 'cat_albums'),
   url(r'^cat/v1/album/state/$', 'cat_album_state'),
   url(r'^cat/v1/album/tag/$', 'cat_tag'),
   url(r'^cat/v1/user/me/$', 'user_me'),
   url(r'^cat/v1/user/favorite/add/$', 'user_favorite_add'),
   url(r'^cat/v1/user/favorite/remove/$', 'user_favorite_remove'),
   url(r'^cat/v1/user/device/register/$', 'cat_register_push'),
   url(r'^cat/v1/user/device/unregister/$', 'cat_deregister_push'),
   url(r'^cat/v1/photo/$', 'cat_photo'),
   url(r'^cat/v1/photo/(?P<photo_id>\d+)/$', 'cat_photo'),
   url(r'^cat/v1/photo/(?P<photo_id>\d+)/(?P<thumb_size>.*)/$', 'cat_photo'),
   url(r'^cat/v1/album_thumb/$', 'cat_album_thumb'),
   url(r'^cat/v1/album_thumb/(?P<album_id>\d+)/$', 'cat_album_thumb'),
   url(r'^cat/v1/album_thumb/(?P<album_id>\d+)/(?P<thumb_size>.*)/$', 'cat_album_thumb'),
)

urlpatterns += patterns('',
   url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^admin_tools/', include('admin_tools.urls')),
   url(r'^i18n/', include('django.conf.urls.i18n')),
   url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs', 'packages': ('project')}),
   url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
)

handler500 = 'project.ajapaik.views.custom_500'
handler404 = 'project.ajapaik.views.custom_404'

if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
    urlpatterns += patterns('', (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )