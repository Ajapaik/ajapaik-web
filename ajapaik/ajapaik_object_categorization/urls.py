from django.conf.urls import url

from ajapaik.ajapaik_object_categorization import views
from ajapaik.ajapaik_object_categorization import api

urlpatterns = [
    url(r'^get-latest-category/(?P<photo_id>\d+)/$', views.get_latest_category,
        name='picture_recognition_get_latest_category')
]


urlpatterns += [
    url(r'^api/v1/annotation/(?P<annotation_id>\d+)/$', api.Category.as_view(),
        name='object_categorization_api_category'),
]