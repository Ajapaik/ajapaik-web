from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.views import serve
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from project.ajapaik.sitemaps import PhotoSitemap, StaticViewSitemap

urlpatterns = patterns('project.ajapaik.views',
   url(r'^logout/', 'logout'),
   url(r'^stream/', 'fetch_stream'),
   url(r'^difficulty-feedback/', 'difficulty_feedback'),
   url(r'^update-comment-count/', 'update_comment_count'),
   url(r'^geotag/add/', 'geotag_add'),
   url(r'^geotag/confirm/', 'geotag_confirm'),
   url(r'^general-info-modal-content/$', 'get_general_info_modal_content', name='general_info_modal_content'),
   url(r'^info-modal-content/$', 'get_album_info_modal_content', name='info_modal_content'),
   url(r'^game/$', 'game', name='game'),
   url(r'^geotag/$', 'game', name='game'),
   url(r'^map/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^pane-contents/$', 'pane_contents'),
   url(r'^map-data/$', 'map_objects_by_bounding_box'),
   url(r'^leaderboard/$', 'leaderboard', name='leaderboard'),
   url(r'^leaderboard/album/(?P<album_id>\d+)/$', 'leaderboard', name='album_leaderboard'),
   url(r'^all-time-leaderboard/$', 'all_time_leaderboard', name='all_time_leaderboard'),
   url(r'^top50/$', 'top50', name='top50'),
   url(r'^top50/album/(?P<album_id>\d+)/$', 'top50', name='album_top50'),
   url(r'^photo/(?P<photo_id>\d+)/upload/$', 'rephoto_upload'),
   url(r'^photo/like/$', 'update_like_state'),
   url(r'^photo-upload-modal/$', 'mapview_photo_upload_modal'),
   url(r'^photo-upload-modal/(?P<photo_id>\d+)/$', 'mapview_photo_upload_modal'),
   url(r'^photo/$', 'photoslug'),
   url(r'^photo/(?P<photo_id>\d+)/$', 'photoslug'),
   url(r'^photo/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
   url(r'^photo-thumb/$', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/$', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/(?P<pseudo_slug>.*)/$', 'image_thumb'),
   url(r'^photo-full/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'image_full'),
   url(r'^photo-selection/$', 'photo_selection', name='photo_selection'),
   url(r'^view-selection/$', 'list_photo_selection', name='list_photo_selection'),
   url(r'^upload-selection/$', 'upload_photo_selection', name='upload_photo_selection'),
   url(r'^$', 'frontpage', name='frontpage'),
   url(r'^photos/$', 'frontpage', name='frontpage_photos'),
   url(r'^photos/(?P<page>\d+)/$', 'frontpage', name='frontpage_photos'),
   url(r'^photos/(?P<album_id>\d+)/(?P<page>\d+)/$', 'frontpage', name='frontpage_photos'),
   url(r'^frontpage-async/$', 'frontpage_async_data'),
   url(r'^frontpage-async-albums/$', 'frontpage_async_albums'),
   url(r'^curator/$', 'curator', name='curator'),
   url(r'^curator-album-info/$', 'curator_get_album_info'),
   url(r'^curator-update-my-album/$', 'curator_update_my_album'),
   url(r'^curator-album-list/$', 'curator_my_album_list'),
   url(r'^curator-selectable-albums/$', 'curator_selectable_albums'),
   url(r'^curator-selectable-parent-albums/$', 'curator_selectable_parent_albums'),
   url(r'^curator-selectable-parent-albums/(?P<album_id>\d+)/$', 'curator_selectable_parent_albums'),
   url(r'^curator-search/$', 'curator_search'),
   url(r'^curator-upload/$', 'curator_photo_upload_handler'),
   url(r'^public-album-create-handler/$', 'public_add_album', name='public_add_album'),
   url(r'^public-area-create-handler/$', 'public_add_area'),
   url(r'^norwegian-csv-upload/$', 'norwegian_csv_upload'),
   url(r'^submit-dating/$', 'submit_dating'),
   url(r'^datings/(?P<photo_id>\d+)/$', 'get_datings'),
   url(r'^choose-upload-action/$', 'photo_upload_choice', name='photo_upload_choice'),
   url(r'^user-upload/$', 'user_upload', name='user_upload'),
   url(r'^user-upload-add-album/$', 'user_upload_add_album', name='user_upload_add_album'),
)

sitemaps = {'photo_permalinks': PhotoSitemap, 'static_pages': StaticViewSitemap}

urlpatterns += patterns('',
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^facebook/(?P<stage>[a-z_]+)/', 'project.ajapaik.facebook.facebook_handler'),
    url(r'^google-login', 'project.ajapaik.google_plus.google_login'),
    url(r'^oauth2callback', 'project.ajapaik.google_plus.auth_return'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs', 'packages': ('project')}),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+).xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

handler500 = 'project.ajapaik.views.custom_500'
handler404 = 'project.ajapaik.views.custom_404'

# FIXME
if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
    urlpatterns += patterns('', (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )