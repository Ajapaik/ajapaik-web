from admin_tools import urls as admin_urls
from allauth import urls as allauth_urls
from django.conf import settings
from django.conf.urls import include, i18n
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.views import serve
from django.urls import re_path, path
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from django.views.i18n import JavaScriptCatalog
from django_comments_xtd import urls as dcxtd_urls

import ajapaik.ajapaik_auth.views as auth_views
import ajapaik.ajapaik_comments.views as comments_views
import ajapaik.ajapaik_curator.views as curator_views
import ajapaik.ajapaik_datings.views as datings_views
import ajapaik.ajapaik_geotags.views as geotags_views
import ajapaik.ajapaik_leaderboard.views as leaderboard_views
import ajapaik.ajapaik_map.views as map_views
import ajapaik.ajapaik_misc.views as misc_views
import ajapaik.ajapaik_profile.api as profile_api_views
import ajapaik.ajapaik_profile.views as profile_views
import ajapaik.ajapaik_similar_photos.views as similar_photos_views
import ajapaik.ajapaik_upload.csv_import.views as csv_import_views
import ajapaik.ajapaik_upload.rephoto.views as rephoto_views
import ajapaik.ajapaik_upload.views as upload_views
import ajapaik.ajapaik_video.views as video_views
from ajapaik.ajapaik import api, delfi, juks, views, iiif
from ajapaik.ajapaik.autocomplete_views import AlbumAutocomplete, AlbumPhotoAutocomplete, AreaAutocomplete, \
    DatingAutocomplete, DatingConfirmationAutocomplete, DeviceAutocomplete, FaceRecognitionRectangleAutocomplete, \
    FaceRecognitionRectangleFeedbackAutocomplete, FaceRecognitionUserSuggestionAutocomplete, \
    FaceRecognitionRectangleSubjectDataSuggestionAutocomplete, GeoTagAutocomplete, \
    GoogleMapsReverseGeocodeAutocomplete, ImageSimilarityAutocomplete, \
    ImageSimilaritySuggestionAutocomplete, LicenceAutocomplete, LocationAutocomplete, \
    ObjectDetectionAnnotationAutocomplete, ObjectAnnotationClassAutocomplete, ObjectAnnotationFeedbackAutocomplete, \
    OpenAlbumAutocomplete, ParentAlbumAutocomplete, PhotoAutocomplete, PointsAutocomplete, ProfileAutocomplete, \
    SkipAutocomplete, SubjectAlbumAutocomplete, SourceAutocomplete, TranscriptionAutocomplete, UserAutocomplete, \
    VideoAutocomplete
from ajapaik.ajapaik.bbox_api import PhotosView
from ajapaik.ajapaik.sitemaps import PhotoSitemap, StaticViewSitemap
from ajapaik.ajapaik_face_recognition import urls as fr_urls
from ajapaik.ajapaik_object_recognition import urls as or_urls

urlpatterns = [
    path('stream/', views.fetch_stream, name='fetch_stream'),
    path('difficulty-feedback/', geotags_views.difficulty_feedback, name='difficulty_feedback'),
    path('geotag/add/', geotags_views.geotag_add, name='geotag_add'),
    path('geotag/confirm/', geotags_views.geotag_confirm, name='geotag_confirm'),
    path('general-info-modal-content/', views.get_general_info_modal_content, name='general_info_modal_content'),
    path('info-modal-content/', views.get_album_info_modal_content, name='info_modal_content'),
    path('game/', geotags_views.game, name='game'),
    path('geotaggers-modal/<int:photo_id>/', geotags_views.geotaggers_modal,
         name='photo_geotaggers'),
    path('geotag/', geotags_views.game, name='game'),
    path('login-modal/', auth_views.login_modal, name='login_modal'),
    path('map/', map_views.mapview, name='map'),
    path('map/photo/<int:photo_id>/', map_views.mapview, name='map'),
    path('map/rephoto/<int:rephoto_id>/', map_views.mapview, name='map'),
    path('map/photo/<int:photo_id>/rephoto/<int:rephoto_id>/', map_views.mapview, name='map'),
    path('map-data/', map_views.map_objects_by_bounding_box, name='map_objects_by_bounding_box'),
    path('leaderboard/', leaderboard_views.leaderboard, name='leaderboard'),
    path('leaderboard/album/<int:album_id>/', leaderboard_views.leaderboard,
         name='album_leaderboard'),
    path('all-time-leaderboard/', leaderboard_views.all_time_leaderboard,
         name='all_time_leaderboard'),
    path('top50/', leaderboard_views.top50, name='top50'),
    path('top50/album/<int:album_id>/', leaderboard_views.top50, name='album_top50'),
    path('photo/<int:photo_id>/upload/', rephoto_views.rephoto_upload,
         name='rephoto_upload'),
    path('photo/<int:photo_id>/info.json/', iiif.photo_info, name='iiif_photo_info'),
    path('photo/<int:photo_id>/manifest.json/', iiif.photo_manifest_v2, name='iiif_photo_manifest_v2'),
    path('photo/<int:photo_id>/v2/manifest.json/', iiif.photo_manifest_v2, name='iiif_photo_manifest_v2'),
    path('photo/like/', views.update_like_state, name='update_like_state'),
    path('photo-upload-modal/<int:photo_id>/', upload_views.photo_upload_modal,
         name='photo_upload_modal'),
    path('photo/<int:photo_id>/', views.photo_slug, name='photo'),
    path('photo/<int:photo_id>/<slug:pseudo_slug>/', views.photo_slug, name='photo'),
    path('video/<int:video_id>/<slug:pseudo_slug>/', video_views.videoslug, name='videoslug'),
    path('video-still/', video_views.generate_still_from_video),
    # Legacy URLs
    path('foto_thumb/', views.redirect_view),
    path('foto_thumb/<int:photo_id>/', views.redirect_view),
    path('foto_thumb/<int:photo_id>/<int:thumb_size>/', views.redirect_view),
    path('foto_thumb/<int:photo_id>/<int:thumb_size>/<slug:pseudo_slug>/', views.redirect_view),
    path('foto_url/<int:photo_id>/', views.redirect_view),
    path('foto_large/<int:photo_id>/', views.redirect_view),
    path('foto_large/<int:photo_id>/<slug:pseudo_slug>/', views.redirect_view),
    path('photo-large/<int:photo_id>/', views.redirect_view),
    path('photo-large/<int:photo_id>/<slug:pseudo_slug>/', views.redirect_view),
    path('photo-url/<int:photo_id>/', views.redirect_view),
    path('photo-url/<int:photo_id>/<slug:pseudo_slug>/', views.redirect_view),
    path('foto/', views.redirect_view, name='legacy_foto'),
    path('foto/<int:photo_id>/', views.redirect_view, name='legacy_foto'),
    path('foto/<int:photo_id>/<slug:pseudo_slug>/', views.redirect_view, name='legacy_foto'),
    path('ajapaikaja/', views.redirect_view, name='legacy_game'),
    path('kaart/', views.redirect_view, name='legacy_map'),
    # Preferred URLs
    path('photo-thumb/<int:photo_id>/', views.image_thumb, name='image_thumb'),
    path('photo-thumb/<int:photo_id>/<int:thumb_size>/', views.image_thumb, name='image_thumb'),
    path('photo-thumb/<int:photo_id>/<int:thumb_size>/<slug:pseudo_slug>/', views.image_thumb,
         name='image_thumb'),
    path('photo-full/<int:photo_id>/<slug:pseudo_slug>/', views.image_full, name='image_full'),
    path('photo-selection/', views.photo_selection, name='photo_selection'),
    path('photo-albums/', views.get_photo_albums, name='get_photo_albums'),
    path('view-selection/', views.list_photo_selection, name='list_photo_selection'),
    path('upload-selection/', views.upload_photo_selection, name='upload_photo_selection'),
    path('', views.frontpage, name='frontpage'),
    path('photos/', views.frontpage, name='frontpage_photos'),
    path('frontpage-async/', views.frontpage_async_data, name='frontpage_async_data'),
    path('frontpage-async-albums/', views.frontpage_async_albums, name='frontpage_async_albums'),
    path('curator/', curator_views.curator, name='curator'),
    path('curator-album-info/', curator_views.curator_get_album_info, name='curator_get_album_info'),
    path('curator-update-my-album/', curator_views.curator_update_my_album,
         name='curator_update_my_album'),
    path('curator-album-list/', curator_views.curator_my_album_list, name='curator_my_album_list'),
    path('curator-selectable-albums/', curator_views.curator_selectable_albums,
         name='curator_selectable_albums'),
    path('curator-search/', curator_views.curator_search, name='curator_search'),
    path('curator-upload/', curator_views.curator_photo_upload_handler,
         name='curator_photo_upload_handler'),
    path('curator-import-list/', curator_views.curator_import_list, name='curator_import_list'),
    path('public-album-create-handler/', views.public_add_album, name='public_add_album'),
    path('public-area-create-handler/', views.public_add_area),
    path('muis-import/', views.muis_import, name='muis_import'),
    path('csv-import/', csv_import_views.csv_import, name='csv_import'),
    path('submit-dating/', datings_views.submit_dating, name='submit_dating'),
    path('datings/<int:photo_id>/', datings_views.get_datings, name='get_datings'),
    path('donate/', misc_views.donate, name='donate'),
    path('choose-upload-action/', views.photo_upload_choice, name='photo_upload_choice'),
    path('user-upload/', upload_views.user_upload, name='user_upload'),
    path('user-upload-add-album/', upload_views.user_upload_add_album, name='user_upload_add_album'),
    path('privacy/', misc_views.privacy, name='privacy'),
    path('terms/', misc_views.terms, name='terms'),
    path('compare-photos/<int:photo_id>/<int:photo_id_2>/', similar_photos_views.compare_photos,
         name='compare-photos'),
    path('compare-all-photos/', similar_photos_views.compare_all_photos, name='compare-all-photos'),
    path('compare-all-photos/<int:photo_id>/<int:photo_id_2>/',
         similar_photos_views.compare_all_photos,
         name='compare-all-photos'),
    path('me/', profile_views.me, name='me'),
    path('user/<int:user_id>/', profile_views.user, name='user'),
    path('user/settings/', profile_views.user_settings, name='user_settings'),
    path('user/settings-modal/', profile_views.user_settings_modal, name='user_settings_modal'),
    path('user/merge-accounts/', profile_views.merge_accounts, name='merge_accounts'),
    path('photo-upload/settings-modal/', profile_views.rephoto_upload_settings_modal,
         name='rephoto_upload_settings_modal'),
    path('supporters/', misc_views.supporters, name='supporters'),
    path('accounts/launcher/', auth_views.oauthdone, name='oauthdone'),
]

urlpatterns += [
    path('api/v1/login/', api.Login.as_view()),
    path('api/v1/register/', api.Register.as_view(), name='api_register'),
    path('api/v1/logout/', api.api_logout.as_view(), name='api_logout'),
    path('api/v1/user/me/', api.api_user_me.as_view()),
    path('api/v1/album/<int:album_id>/', api.AlbumNearestPhotos.as_view()),
    path('api/v1/album/<int:album_id>/information/', api.AlbumInformation.as_view(), name='api_album_information'),
    path(
        'api/v1/album/<int:album_id>/photo/<int:photo_id>/',
        api.AlbumPhotoInformation.as_view(),
        name='api_albumphoto_information'
    ),
    path('api/v1/album/nearest/', api.AlbumNearestPhotos.as_view()),
    path('api/v1/finna/nearest/', api.FinnaNearestPhotos.as_view()),
    path('api/v1/album/state/', api.AlbumPhotos.as_view()),
    path('api/v1/source/', api.SourceDetails.as_view()),
    path('api/v1/album/photos/search/', api.PhotosInAlbumSearch.as_view()),
    path('api/v1/album_thumb/<int:album_id>/', api.api_album_thumb, name='api_album_thumb'),
    path('api/v1/album_thumb/<int:album_id>/<int:thumb_size>', api.api_album_thumb, name='api_album_thumb'),
    path('api/v1/albums/', api.AlbumList.as_view()),
    path('api/v1/albums/search/', api.AlbumsSearch.as_view()),
    path('api/v1/wikidocumentaries/', api.WikidocsAlbumsSearch.as_view()),
    path('api/v1/wikidocumentaries/photos/', api.WikidocsAlbumSearch.as_view()),
    path('api/v1/photo/applied-operations/', api.PhotoAppliedOperations.as_view(),
         name='api_photo_applied_operations'),
    path('api/v1/photo/applied-operations/<int:photo_id>/', api.PhotoAppliedOperations.as_view(),
         name='api_photo_applied_operations'),
    path('api/v1/photo/suggestion/', api.PhotoSuggestion.as_view(), name='api_photo_suggestion'),
    path('api/v1/photo/suggestion/<int:photo_id>/', api.PhotoSuggestion.as_view(), name='api_photo_suggestion'),
    path('api/v1/photo/state/', api.PhotoDetails.as_view()),
    path('api/v1/photo/activity-log/', api.PhotoActivityLog.as_view()),
    path('api/v1/photo/upload/', api.RephotoUpload.as_view(), name='api_photo_upload'),
    path('api/v1/photo/upload/settings', api.RephotoUploadSettings.as_view(),
         name='api_submit_rephoto_upload_settings'),
    path('api/v1/photo/favorite/set/', api.ToggleUserFavoritePhoto.as_view()),
    path('api/v1/photo/fetch-hkm-finna/', api.FetchFinnaPhoto.as_view()),
    path('api/v1/photos/favorite/order-by-distance-to-location/', api.UserFavoritePhotoList.as_view()),
    path('api/v1/photos/filtered/rephotographed-by-user/', api.PhotosWithUserRephotos.as_view()),
    path('api/v1/photos/search/', api.PhotosSearch.as_view()),
    path('api/v1/photos/search/user-rephotos/', api.UserRephotosSearch.as_view()),
    path('api/v1/photos/similar/', api.SubmitSimilarPhotos.as_view(), name='api_submit_similarity'),
    path('api/v1/transcriptions/<int:photo_id>/', api.Transcriptions.as_view(), name='api_transcriptions'),
    path('api/v1/transcriptions/', api.Transcriptions.as_view(), name='api_submit_transcription'),
    path('api/v1/transcription-feedback/', api.SubmitTranscriptionFeedback.as_view(),
         name='api_confirm_transcription'),
    path('api/v1/change-profile-display-name', api.ChangeProfileDisplayName.as_view(),
         name='api_change_profile_display_name'),
    path('api/v1/user-settings/', api.UserSettings.as_view(), name='api_submit_user_settings'),
    path('api/v1/merge-profiles/', profile_api_views.MergeProfiles.as_view(), name='api_merge_users')
]

urlpatterns += [
    path('delfi-api/v1/photo/', delfi.photo_info),
    path('delfi_api/v1/photo/', delfi.photo_info),
    path('delfi-api/v1/photos-bbox/', delfi.photos_bbox),
    path('delfi_api/v1/photos_bbox/', delfi.photos_bbox),
]

urlpatterns += [
    path('bbox/v1/', PhotosView.as_view())
]

urlpatterns += [
    path('juks/empty-json/', juks.empty_json),
    path('juks/layers/', juks.layers),
]

sitemaps = {
    'photo_permalinks': PhotoSitemap,
    'static_pages': StaticViewSitemap
}

urlpatterns += [
    re_path(f'{settings.STATIC_URL}(?P<path>.*)$/', cache_page(86400)(serve),
            {'show_indexes': True, 'insecure': True}),
    path('accounts/email/', profile_views.MyEmailView.as_view(), name="account_email"),
    path('accounts/password/change/', profile_views.MyPasswordChangeView.as_view(),
         name="account_change_password"),
    path('accounts/password/set/', profile_views.MyPasswordSetView.as_view(),
         name="account_set_password"),
    path('accounts/social/connections/', profile_views.MyConnectionsView.as_view(),
         name="socialaccount_connections"),
    path('accounts/', include(allauth_urls)),
    path('admin/', admin.site.urls),
    path('admin_tools/', include(admin_urls)),
    path('comments/for/<int:photo_id>/', comments_views.CommentList.as_view(),
         name='comments-for-photo'),
    path('comments/post-one/<int:photo_id>/', login_required(comments_views.PostComment.as_view()),
         name='comments-post-one'),
    path('comments/delete-one/', login_required(comments_views.DeleteComment.as_view()),
         name='comments-delete-one'),
    path('comments/edit-one/', login_required(comments_views.EditComment.as_view()),
         name='comments-edit-one'),
    path('comments/like-count/<int:comment_id>/', comments_views.get_comment_like_count,
         name='comments-like-count'),
    path('comments/', include(dcxtd_urls)),
    path('i18n/', include(i18n)),
    path('jsi18n/', cache_page(86400)(JavaScriptCatalog.as_view(packages=['ajapaik.ajapaik'], domain='djangojs')),
         name='javascript-catalog'),
    path('feed/photos/', RedirectView.as_view(url='http://api.ajapaik.ee/?action=photo&format=atom', permanent=True),
         name='feed'),
    # path('sitemap.xml', cache_page(86400)(sitemap_views.index), {'sitemaps': sitemaps}),
    # path('sitemap-<str:section>.xml', cache_page(86400)(sitemap_views.sitemap), {'sitemaps': sitemaps},
    #     name='django.contrib.sitemaps.views.sitemap'),
    path('face-recognition/', include(fr_urls)),
    path('object-recognition/', include(or_urls))
]

if hasattr(settings, 'GOOGLE_ANALYTICS_KEY'):
    urlpatterns += [
        path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    ]
else:
    urlpatterns += [
        path('robots.txt', TemplateView.as_view(template_name='robots-staging.txt', content_type='text/plain')),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('vanalinnad.mooo.com/(.*)', document_root=settings.VANALINNAD_ROOT)

urlpatterns += [
    path('autocomplete/album-autocomplete/', AlbumAutocomplete.as_view(), name='album-autocomplete'),
    path('autocomplete/album-photo-autocomplete/', AlbumPhotoAutocomplete.as_view(),
         name='album-photo-autocomplete'),
    path('autocomplete/area-autocomplete/', AreaAutocomplete.as_view(), name='area-autocomplete'),
    path('autocomplete/dating-autocomplete/', DatingAutocomplete.as_view(), name='dating-autocomplete'),
    path('autocomplete/dating_confirmation-autocomplete/', DatingConfirmationAutocomplete.as_view(),
         name='dating-confirmation-autocomplete'),
    path('autocomplete/device-autocomplete/', DeviceAutocomplete.as_view(), name='device-autocomplete'),
    path('autocomplete/face-recognition-rectangle-autocomplete/', FaceRecognitionRectangleAutocomplete.as_view(),
         name='face-recognition-rectangle-autocomplete'),
    path('autocomplete/face-recognition-rectangle-feedback-autocomplete/',
         FaceRecognitionRectangleFeedbackAutocomplete.as_view(),
         name='face-recognition-rectangle-feedback-autocomplete'),
    path('autocomplete/face-recognition-user-suggestion-autocomplete/',
         FaceRecognitionUserSuggestionAutocomplete.as_view(), name='face-recognition-user-suggestion-autocomplete'),
    path('autocomplete/face-recognition-rectangle-subject-data-suggestion-autocomplete/',
         FaceRecognitionRectangleSubjectDataSuggestionAutocomplete.as_view(),
         name='face-recognition-rectangle-subject-data-suggestion-autocomplete'),
    path('autocomplete/geotag-autocomplete/', GeoTagAutocomplete.as_view(), name='geotag-autocomplete'),
    path('autocomplete/google-reverse-geocode-autocomplete/',
         GoogleMapsReverseGeocodeAutocomplete.as_view(),
         name='google-reverse-geocode-autocomplete'
         ),
    path('autocomplete/image-similarity-autocomplete/', ImageSimilarityAutocomplete.as_view(),
         name='image-similarity-autocomplete'),
    path('autocomplete/image-similarity-suggestion-autocomplete/', ImageSimilaritySuggestionAutocomplete.as_view(),
         name='image-similarity-suggestion-autocomplete'),
    path('autocomplete/location/', LocationAutocomplete.as_view(), name='location-autocomplete'),
    path('autocomplete/licence-autocomplete/', LicenceAutocomplete.as_view(), name='licence-autocomplete'),
    path('autocomplete/object-detection-annotation-autocomplete/', ObjectDetectionAnnotationAutocomplete.as_view(),
         name='object-detection-annotation-autocomplete'),
    path('autocomplete/object-annotation-class-autocomplete/', ObjectAnnotationClassAutocomplete.as_view(),
         name='object-annotation-class-autocomplete'),
    path('autocomplete/object-annotation-feedback-autocomplete/', ObjectAnnotationFeedbackAutocomplete.as_view(),
         name='object-annotation-feedback-autocomplete'),
    path('autocomplete/photo-autocomplete/', PhotoAutocomplete.as_view(), name='photo-autocomplete'),
    path('autocomplete/points-autocomplete/', PointsAutocomplete.as_view(), name='points-autocomplete'),
    path('autocomplete/profile-autocomplete/', ProfileAutocomplete.as_view(), name='profile-autocomplete'),
    path('autocomplete/open-album-autocomplete/', OpenAlbumAutocomplete.as_view(), name='open-album-autocomplete'),
    path('autocomplete/parent-album-autocomplete/', ParentAlbumAutocomplete.as_view(),
         name='open-album-autocomplete'),
    path('autocomplete/skip-autocomplete/', SkipAutocomplete.as_view(), name='skip-autocomplete'),
    path('autocomplete/source-autocomplete/', SourceAutocomplete.as_view(), name='source-autocomplete'),
    path('autocomplete/subject-album-autocomplete/', SubjectAlbumAutocomplete.as_view(),
         name='subject-album-autocomplete'),
    path('autocomplete/transcription-autocomplete/', TranscriptionAutocomplete.as_view(),
         name='transcription-autocomplete'),
    path('autocomplete/user-autocomplete/', UserAutocomplete.as_view(), name='user-autocomplete'),
    path('autocomplete/video-autocomplete/', VideoAutocomplete.as_view(), name='video-autocomplete'),
]
