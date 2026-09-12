from django.urls import path

from ajapaik.ajapaik_face_recognition import api
from ajapaik.ajapaik_face_recognition import views

urlpatterns = [
    path('add-subject/', views.add_subject, name='face_recognition_add_subject'),
    path('annotation/<int:annotation_id>/feedback/', views.add_rectangle_feedback,
         name='face_annotation_add_feedback'),
    path('update-annotation/<int:annotation_id>/', views.update_annotation, name='face_annotation_update'),
    path('remove-annotation/<int:annotation_id>/', views.remove_annotation, name='face_annotation_remove'),
    path('subject-data/', views.get_subject_data, name='face_recognition_subject_data'),
    path('subject-data/<int:rectangle_id>/', views.get_subject_data, name='face_recognition_subject_data'),
    path('subject-data/empty/', views.get_subject_data_empty, name='face_recognition_subject_data_empty')
]

urlpatterns += [
    path('api/v1/annotation/<int:annotation_id>/', api.Annotation.as_view(),
         name='face_recognition_api_annotation'),
    path('api/v1/subject-data/', api.AddSubjectData.as_view(), name='face_recognition_api_subject_data'),
    path('api/v1/album-has-annotations/<int:album_id>/', api.AlbumData.as_view(),
         name='face_recognition_api_album_data')
]
