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
   url(r'^info_modal_content/$', 'get_album_info_modal_content', name='info_modal_content'),
   url(r'^info_modal_content/(?P<album_id>\d+)/$', 'get_album_info_modal_content', name='info_modal_content'),
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
   url(r'^leaderboard/album/(?P<album_id>\d+)/$', 'leaderboard', name='album_leaderboard'),
   url(r'^all-time-leaderboard/$', 'all_time_leaderboard', name='all_time_leaderboard'),
   url(r'^top50/$', 'top50', name='top50'),
   url(r'^top50/album/(?P<album_id>\d+)/$', 'top50', name='album_top50'),
   url(r'^heatmap_data/$', 'heatmap_data'),
   url(r'^foto/(?P<photo_id>\d+)/upload/$', 'photo_upload'),
   url(r'^photo_upload_modal/(?P<photo_id>\d+)/$', 'mapview_photo_upload_modal'),
   url(r'^foto/$', 'photo', name="photo"),
   url(r'^foto/(?P<photo_id>\d+)/$', 'photo', name="photo"),
   url(r'^foto/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
   url(r'^foto_large/(?P<photo_id>\d+)/$', 'photo_large'),
   url(r'^foto_url/(?P<photo_id>\d+)/$', 'photo_url'),
   url(r'^foto_thumb/(?P<photo_id>\d+)/$', 'photo_thumb', name="photo_thumb"),
   url(r'^foto_thumb/(?P<photo_id>\d+)/(?P<thumb_size>.*)/', 'photo_thumb', name="photo_thumb"),
   url(r'^$', 'frontpage_bootstrap', name='frontpage'),
   url(r'^photos/$', 'frontpage_bootstrap', name='frontpage_photos'),
   url(r'^grid/$', 'grid'),
   url(r'^grid_infinity/$', 'grid_infinite_scroll'),
   url(r'^frontpage_infinity/$', 'frontpage_infinite_scroll'),
   url(r'^curator/$', 'curator'),
   url(r'^curator_album_info/$', 'curator_get_album_info'),
   url(r'^curator_update_my_album/$', 'curator_update_my_album'),
   url(r'^curator_album_list/$', 'curator_my_album_list'),
   url(r'^curator_selectable_albums/$', 'curator_selectable_albums'),
   url(r'^curator_search/$', 'curator_search'),
   url(r'^curator_upload/$', 'curator_photo_upload_handler'),
   # url(r'^public_photo_upload/$', 'public_photo_upload'),
   # url(r'^public_photo_upload_handler/$', 'public_photo_upload_handler'),
   url(r'^public_album_create_handler/$', 'public_add_album'),
   url(r'^public_area_create_handler/$', 'public_add_area'),
   # url(r'^public_photo_delete_handler/(?P<photo_id>\d+)/$', 'delete_public_photo'),
   # url(r'^csv_upload/$', 'csv_upload'),
   # url(r'^europeana/$', 'europeana'),
   # url(r'^locloud_locator/$', 'locloud_locator'),
)

urlpatterns += patterns('project.home.cat',
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
   url(r'^cat/v1/photo/(?P<photo_id>\d+)/$', 'cat_photo'),
   url(r'^cat/v1/photo/(?P<photo_id>\d+)/(?P<thumb_size>.*)/$', 'cat_photo'),
   url(r'^cat/v1/album_thumb/(?P<album_id>\d+)/$', 'cat_album_thumb'),
   url(r'^cat/v1/album_thumb/(?P<album_id>\d+)/(?P<thumb_size>.*)/$', 'cat_album_thumb'),
   url(r'^cat/v1/results/$', 'cat_results'),
   url(r'^cat/v1/results/(?P<page>\d+)/$', 'cat_results')
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

handler500 = 'project.home.views.custom_500'
handler404 = 'project.home.views.custom_404'

if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
    urlpatterns += patterns('', (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )