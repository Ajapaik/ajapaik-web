from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers
from project.home.photo_import import PhotoViewSet, AreaViewSet, SourceViewSet, AlbumViewSet
from project.sitemaps import PhotoSitemap, StaticViewSitemap

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'api/photos', PhotoViewSet)
router.register(r'api/areas', AreaViewSet)
router.register(r'api/albums', AlbumViewSet)
router.register(r'api/sources', SourceViewSet)

# TODO: Locale specific URLs
urlpatterns = patterns('project.home.views',
   url(r'^logout/', 'logout'),
   url(r'^stream/', 'fetch_stream'),
   url(r'^difficulty_feedback/', 'difficulty_feedback'),
   # url(r'^log_user_map_action/', 'log_user_map_action'),
   url(r'^geotag/add/', 'geotag_add'),
   url(r'^ajapaikaja/$', 'game', name='game'),
   url(r'^game/$', 'game', name='game'),
   url(r'^kaart/$', 'mapview', name='map'),
   url(r'^map/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^pane_contents/$', 'pane_contents'),
   url(r'^map_data/$', 'map_objects_by_bounding_box'),
   url(r'^leaderboard/$', 'leaderboard', name='leaderboard'),
   url(r'^top50/$', 'top50', name='top50'),
   url(r'^heatmap_data/$', 'heatmap_data'),
   url(r'^foto/(?P<photo_id>\d+)/upload/$', 'photo_upload'),
   url(r'^photo_upload_modal/(?P<photo_id>\d+)/$', 'mapview_photo_upload_modal'),
   url(r'^foto/(?P<photo_id>\d+)/$', 'photo', name="photo"),
   url(r'^foto/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
   url(r'^foto_large/(?P<photo_id>\d+)/$', 'photo_large'),
   url(r'^foto_url/(?P<photo_id>\d+)/$', 'photo_url'),
   url(r'^foto_thumb/(?P<photo_id>\d+)/$', 'photo_thumb', name="photo_thumb"),
   url(r'^foto_thumb/(?P<photo_id>\d+)/(?P<thumb_size>.*)/', 'photo_thumb', name="photo_thumb"),
   url(r'^$', 'frontpage', name='frontpage'),
   # url(r'^grid/$', 'grid'),
   # url(r'^grid_infinity/$', 'grid_infinite_scroll'),
   url(r'^curator/$', 'curator'),
   url(r'^check/$', 'check_if_photo_in_ajapaik'),
   url(r'^curator_album_list/$', 'curator_my_album_list'),
   url(r'^curator_selectable_albums/$', 'curator_selectable_albums'),
   url(r'^curator_search/$', 'curator_search'),
   url(r'^curator_upload/$', 'curator_photo_upload_handler'),
   url(r'^public_photo_upload/$', 'public_photo_upload'),
   url(r'^public_photo_upload_handler/$', 'public_photo_upload_handler'),
   url(r'^public_album_create_handler/$', 'public_add_album'),
   url(r'^public_area_create_handler/$', 'public_add_area'),
   url(r'^public_photo_delete_handler/(?P<photo_id>\d+)/$', 'delete_public_photo'),
   url(r'^csv_upload/$', 'csv_upload'),
   # url(r'^europeana/$', 'europeana'),
   # url(r'^locloud_locator/$', 'locloud_locator'),
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
   url(r'^feed/photos/', RedirectView.as_view(url='http://api.ajapaik.ee/?action=photo&format=atom'), name='feed'),
   url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'photo_permalinks': PhotoSitemap, 'static_pages': StaticViewSitemap}}, name='django.contrib.sitemaps.views.sitemap'),
   url(r'^', include(router.urls)),
   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')))

# handler500 = 'project.home.views.custom_500'
# handler404 = 'project.home.views.custom_404'

#TODO: Why?
if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
    urlpatterns += patterns('', (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )