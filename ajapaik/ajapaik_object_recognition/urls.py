from django.urls import path

from ajapaik.ajapaik_object_recognition import api
from ajapaik.ajapaik_object_recognition import views

urlpatterns = [
    path('get-object-annotation-classes/', views.get_object_annotation_classes, name='object_annotation_get_classes'),
    path('add-annotation/', views.add_annotation, name='object_detection_add_annotation'),
    path('update-annotation/', views.update_annotation, name='object_detection_update_annotation'),
    path('remove-annotation/<int:annotation_id>/', views.remove_annotation,
         name='object_detection_update_annotation'),
    path('annotation/<int:annotation_id>/feedback/', views.add_feedback, name='object_annotation_feedback'),
    path('get-all-face-and-object-annotations/<int:photo_id>/', views.get_all_annotations,
         name='object_detection_get_all_annotations'),
]

urlpatterns += [
    path('api/v1/annotation/<int:annotation_id>/', api.Annotation.as_view(),
         name='object_recognition_api_annotation'),
]
