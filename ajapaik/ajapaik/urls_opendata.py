from django.urls import re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from ajapaik.ajapaik.opendata import PhotoViewSet, PhotoGeoTagViewSet

router = DefaultRouter()
router.register(r'photos', PhotoViewSet)

urlpatterns = router.urls

urlpatterns += format_suffix_patterns([
    re_path(r'^photos/(?P<pk>[0-9]+)/geotags/$',
            PhotoGeoTagViewSet.as_view({'get': 'retrieve'}),
            name='opendata-photo-geotags'),
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
])
