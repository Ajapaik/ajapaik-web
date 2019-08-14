from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get-object-annotation-classes', views.get_object_annotation_classes, name='object_annotation_get_classes'),
    url(r'^add-annotation', views.add_annotation, name='object_detection_add_annotation'),
    url(r'^update-annotation', views.update_annotation, name='object_detection_update_annotation'),
    url(r'^remove-annotation/(?P<annotation_id>\d+)', views.remove_annotation, name='object_detection_update_annotation'),
    url(r'^annotation/(?P<annotation_id>\d+)/feedback/$', views.add_feedback, name='object_annotation_feedback'),
    url(r'^get-all-face-and-object-annotations/(?P<photo_id>\d+)/$', views.get_all_annotations,
        name='object_detection_get_all_annotations')
]
