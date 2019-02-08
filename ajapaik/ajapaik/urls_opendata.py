from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from ajapaik.ajapaik.opendata import PhotoViewSet, PhotoGeoTagViewSet

router = DefaultRouter()
router.register(r'photos', PhotoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]

urlpatterns += format_suffix_patterns([
    url(r'^photos/(?P<pk>[0-9]+)/geotags/$',
        PhotoGeoTagViewSet.as_view({'get': 'retrieve'}),
        name='opendata-photo-geotags'),
])
