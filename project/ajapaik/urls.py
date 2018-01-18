from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.views import serve
from django.views.generic import RedirectView, TemplateView

from project.ajapaik.bbox_api import PhotosView
from project.ajapaik.sitemaps import PhotoSitemap, StaticViewSitemap
from project.ajapaik import views
from project.ajapaik import api

urlpatterns = patterns('project.ajapaik.views',
   url(r'^logout/', 'logout'),
   url(r'^stream/', 'fetch_stream'),
   url(r'^difficulty-feedback/', 'difficulty_feedback'),
   url(r'^geotag/add/', 'geotag_add'),
   url(r'^geotag/confirm/', 'geotag_confirm'),
   url(r'^general-info-modal-content/$', 'get_general_info_modal_content', name='general_info_modal_content'),
   url(r'^info-modal-content/$', 'get_album_info_modal_content', name='info_modal_content'),
   url(r'^ajapaikaja/$', 'game', name='game'),
   url(r'^game/$', 'game', name='game'),
   url(r'^geotag/$', 'game', name='game'),
   url(r'^kaart/$', 'mapview', name='map'),
   url(r'^map/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^map/photo/(?P<photo_id>\d+)/rephoto/(?P<rephoto_id>\d+)/$', 'mapview', name='map'),
   url(r'^map-data/$', 'map_objects_by_bounding_box'),
   url(r'^leaderboard/$', 'leaderboard', name='leaderboard'),
   url(r'^leaderboard/album/(?P<album_id>\d+)/$', 'leaderboard', name='album_leaderboard'),
   url(r'^all-time-leaderboard/$', 'all_time_leaderboard', name='all_time_leaderboard'),
   url(r'^top50/$', 'top50', name='top50'),
   url(r'^top50/album/(?P<album_id>\d+)/$', 'top50', name='album_top50'),
   url(r'^foto/(?P<photo_id>\d+)/upload/$', 'rephoto_upload'),
   url(r'^photo/(?P<photo_id>\d+)/upload/$', 'rephoto_upload'),
   url(r'^photo/like/$', 'update_like_state'),
   url(r'^photo-upload-modal/$', 'mapview_photo_upload_modal'),
   url(r'^photo-upload-modal/(?P<photo_id>\d+)/$', 'mapview_photo_upload_modal'),
   url(r'^foto/$', 'photoslug', name='foto'),
   url(r'^foto/(?P<photo_id>\d+)/$', 'photoslug', name="foto"),
   url(r'^foto/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
   url(r'^photo/$', 'photoslug'),
   url(r'^photo/(?P<photo_id>\d+)/$', 'photoslug'),
   url(r'^photo/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'photoslug'),
   url(r'^video/(?P<video_id>\d+)/(?P<pseudo_slug>.*)/$', 'videoslug'),
   url(r'^video-still/$', 'generate_still_from_video'),
   # Legacy URLs
   url(r'^foto_thumb/$', 'image_thumb'),
   url(r'^foto_thumb/(?P<photo_id>\d+)/$', 'image_thumb'),
   url(r'^foto_thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/', 'image_thumb'),
   url(r'^foto_thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/(?P<pseudo_slug>.*)/$', 'image_thumb'),
   url(r'^foto_url/(?P<photo_id>\d+)/$', 'image_thumb'),
   url(r'^foto_large/(?P<photo_id>\d+)/$', 'image_full'),
   url(r'^foto_large/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'image_full'),
   url(r'^photo-large/(?P<photo_id>\d+)/$', 'image_full'),
   url(r'^photo-large/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'image_full'),
   url(r'^photo-url/(?P<photo_id>\d+)/$', 'image_thumb'),
   url(r'^photo-url/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'image_thumb'),
   # Preferred URLs
   url(r'^photo-thumb/$', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/$', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/', 'image_thumb'),
   url(r'^photo-thumb/(?P<photo_id>\d+)/(?P<thumb_size>\d+)/(?P<pseudo_slug>.*)/$', 'image_thumb'),
   url(r'^photo-full/(?P<photo_id>\d+)/(?P<pseudo_slug>.*)/$', 'image_full'),
   url(r'^photo-selection/$', 'photo_selection', name="photo_selection"),
   url(r'^view-selection/$', 'list_photo_selection', name="list_photo_selection"),
   url(r'^upload-selection/$', 'upload_photo_selection', name="upload_photo_selection"),
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
   url(r'^csv-upload/$', 'csv_upload'),
   url(r'^norwegian-csv-upload/$', 'norwegian_csv_upload'),
   url(r'^uudiskiri/$', 'newsletter', name='uudiskiri'),
   url(r'^uudiskiri/(?P<slug>.*)/$', 'newsletter'),
   url(r'^submit-dating/$', 'submit_dating'),
   url(r'^datings/(?P<photo_id>\d+)/$', 'get_datings'),
   url(r'^donate/$', 'donate', name='donate'),
   url(r'^choose-upload-action/$', 'photo_upload_choice', name='photo_upload_choice'),
   url(r'^user-upload/$', 'user_upload', name='user_upload'),
   url(r'^user-upload-add-album/$', 'user_upload_add_album', name='user_upload_add_album'),
   url(r'^privacy/$', 'privacy', name='privacy'),
   url(r'^terms/$', 'terms', name='terms'),
)


urlpatterns += patterns('project.ajapaik.api',
    url(r'^api/v1/login/$', 'api_login'),
    url(r'^api/v1/register/$', 'api_register', name='api_register'),
    url(r'^api/v1/logout/$', 'api_logout'),
    url(r'^api/v1/user/me/$', 'api_user_me'),
    url(r'^api/v1/album/nearest/$', api.AlbumNearest.as_view()),
    url(r'^api/v1/album/state/$', api.AlbumDetails.as_view()),
    url(r'^api/v1/album_thumb/(?P<album_id>\d+)/$', 'api_album_thumb'),
    url(r'^api/v1/album_thumb/(?P<album_id>\d+)/(?P<thumb_size>.*)/$', 'api_album_thumb'),
    url(r'^api/v1/albums/$', 'api_albums'),
    url(r'^api/v1/photo/upload/$', 'api_photo_upload', name='api_photo_upload'),
    url(r'^api/v1/photo/state/$', api.PhotoDetails.as_view()),
    url(r'^api/v1/photo/favorite/set/$', api.ToggleUserFavoritePhoto.as_view()),
    url(r'^api/v1/photos/favorite/order-by-distance-to-location/$', api.UserFavoritePhotoList.as_view()),
)

urlpatterns += patterns('project.ajapaik.delfi',
    url(r'^delfi-api/v1/photo/$', 'photo_info'),
    url(r'^delfi_api/v1/photo/$', 'photo_info'),
    url(r'^delfi-api/v1/photos-bbox/$', 'photos_bbox'),
    url(r'^delfi_api/v1/photos_bbox/$', 'photos_bbox'),
)

urlpatterns += patterns('project.ajapaik.bbox_api',
    url(r'^bbox/v1/$', PhotosView.as_view())
)

urlpatterns += patterns('project.ajapaik.then_and_now_tours',
    url(r'^then-and-now-tours/$', 'frontpage'),
    url(r'^then-and-now-tours/create-tour-1/$', 'create_tour_step_1'),
    url(r'^then-and-now-tours/markers-for-step-2/$', 'get_markers_for_create_step_2'),
    url(r'^then-and-now-tours/toggle-photo-selection/$', 'toggle_photo_selection'),
    url(r'^then-and-now-tours/create-tour-2/(?P<tour_id>\d+)/$', 'create_tour_step_2'),
    url(r'^then-and-now-tours/create-tour-3/(?P<tour_id>\d+)/$', 'create_tour_step_3'),
    url(r'^then-and-now-tours/create-tour-4/(?P<tour_id>\d+)/$', 'create_tour_step_4'),
    url(r'^then-and-now-tours/create-tour-5/(?P<tour_id>\d+)/$', 'create_tour_step_5'),
    url(r'^then-and-now-tours/generate-ordered-tour/$', 'generate_ordered_tour'),
    url(r'^then-and-now-tours/map/(?P<tour_id>\d+)/$', 'map_view'),
    url(r'^then-and-now-tours/map/', 'map_view'),
    url(r'^then-and-now-tours/get-map-markers/(?P<tour_id>\d+)/$', 'get_map_markers'),
    url(r'^then-and-now-tours/get-gallery-photos/(?P<tour_id>\d+)/$', 'get_gallery_photos'),
    url(r'^then-and-now-tours/detail/(?P<tour_id>\d+)/(?P<photo_id>\d+)/$', 'detail'),
    url(r'^then-and-now-tours/detail/(?P<tour_id>\d+)/(?P<photo_id>\d+)/(?P<rephoto_id>\d+)/$', 'detail'),
    url(r'^then-and-now-tours/rephoto-thumb/(?P<rephoto_id>\d+)/(?P<thumb_size>\d+)/(?P<pseudo_slug>.*)/$', 'rephoto_thumb'),
    url(r'^then-and-now-tours/rephoto-thumb/(?P<rephoto_id>\d+)/(?P<pseudo_slug>.*)/$', 'rephoto_thumb'),
    url(r'^then-and-now-tours/gallery/(?P<tour_id>\d+)/$', 'gallery'),
    url(r'^then-and-now-tours/camera/upload/$', 'camera_upload'),
    url(r'^then-and-now-tours/tour-complete/(?P<tour_id>\d+)/$', 'tour_complete'),
    url(r'^then-and-now-tours/participants/(?P<tour_id>\d+)/$', 'participants'),
    url(r'^then-and-now-tours/choose-group/(?P<tour_id>\d+)/$', 'choose_group'),
    url(r'^then-and-now-tours/manage/(?P<tour_id>\d+)/$', 'manage'),
    url(r'^then-and-now-tours/settings/(?P<tour_id>\d+)/$', 'settings'),
    url(r'^then-and-now-tours/my-tours/(?P<tour_id>\d+)/$', 'my_tours'),
    url(r'^then-and-now-tours/delete-tour/$', 'delete_tour'),
    url(r'^then-and-now-tours/delete-rephoto/$', 'delete_rephoto'),
    url(r'^then-and-now-tours/toggle-rephoto-open/$', 'toggle_rephoto_open'),
    url(r'^then-and-now-tours/my-tours/$', 'my_tours'),
    url(r'^then-and-now-tours/my-rephotos/(?P<tour_id>\d+)/$', 'my_rephotos'),
    url(r'^then-and-now-tours/send-rephoto-to-ajapaik/(?P<tour_rephoto_id>\d+)/$', 'send_rephoto_to_ajapaik'),
)

urlpatterns += patterns('project.ajapaik.juks',
    url(r'^juks/empty-json/$', 'empty_json'),
    url(r'^juks/layers/$', 'layers'),
)

sitemaps = {'photo_permalinks': PhotoSitemap, 'static_pages': StaticViewSitemap}

urlpatterns += patterns('',
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve, {'show_indexes': True, 'insecure': False}),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^comments/for/(?P<photo_id>\d+)/$', views.CommentList.as_view(), name='comments-for-photo'),
    url(r'^comments/post-one/(?P<photo_id>\d+)/$', login_required(views.PostComment.as_view()), name='comments-post-one'),
    url(r'^comments/delete-one/$', login_required(views.DeleteComment.as_view()), name='comments-delete-one'),
    url(r'^comments/edit-one/$', login_required(views.EditComment.as_view()), name='comments-edit-one'),
    url(r'^comments/like-count/(?P<comment_id>\d+)/$', views.get_comment_like_count, name='comments-like-count'),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'^facebook/(?P<stage>[a-z_]+)/', 'project.ajapaik.facebook.facebook_handler'),
    url(r'^google-login', 'project.ajapaik.google_plus.google_login'),
    url(r'^oauth2callback', 'project.ajapaik.google_plus.auth_return'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs', 'packages': ('project')}),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    url(r'^feed/photos/', RedirectView.as_view(url='http://api.ajapaik.ee/?action=photo&format=atom', permanent=True), name='feed'),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+).xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

handler500 = 'project.ajapaik.views.custom_500'
handler404 = 'project.ajapaik.views.custom_404'

if settings.GOOGLE_ANALYTICS_KEY == 'UA-21689048-1':
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), )
else:
    urlpatterns += patterns('', (r'^robots\.txt$', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')), )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
    urlpatterns += patterns('', (r'^media/(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}), )
    urlpatterns += patterns('', (r'^vanalinnad.mooo.com/(.*)', 'django.views.static.serve', {'document_root': settings.VANALINNAD_ROOT, 'show_indexes': True}), )
