from django.conf.urls import url

from ajapaik.ajapaik_face_recognition import api
from ajapaik.ajapaik_face_recognition import views

urlpatterns = [
    url(r'^add-subject/$', views.add_subject, name='face_recognition_add_subject'),
    url(r'^annotation/(?P<annotation_id>\d+)/feedback/$', views.add_rectangle_feedback,
        name='face_annotation_add_feedback'),
    url(r'^update-annotation/(?P<annotation_id>\d+)/$', views.update_annotation, name='face_annotation_update'),
    url(r'^remove-annotation/(?P<annotation_id>\d+)/$', views.remove_annotation, name='face_annotation_remove'),
    url(r'^subject-data/$', views.get_subject_data, name='face_recognition_subject_data'),
    url(r'^subject-data/(?P<rectangle_id>\d+)/$', views.get_subject_data, name='face_recognition_subject_data'),
    url(r'^subject-data/empty/$', views.get_subject_data_empty, name='face_recognition_subject_data_empty')
]

urlpatterns += [
    url(r'^api/v1/annotation/(?P<annotation_id>\d+)/$', api.Annotation.as_view(),
        name='face_recognition_api_annotation'),
    url(r'^api/v1/subject-data/$', api.AddSubjectData.as_view(), name='face_recognition_api_subject_data'),
    url(r'^api/v1/album-has-annotations/(?P<album_id>\d+)/$', api.AlbumData.as_view(),
        name='face_recognition_api_album_data')
]
