from django.conf.urls import url

from ajapaik.ajapaik_object_categorization import views

urlpatterns = [
    url(r'^get-latest-category/(?P<photo_id>\d+)/$', views.get_latest_category_from_result_table,
        name='picture_recognition_get_latest_category'),
    url(r'^confirm-latest-category', views.propose_alternative_category,
        name='picture_recognition_get_latest_category'),
    url(r'^publish-picture-category-result', views.post_image_category_result_table,
        name='publish_picture_category_result'),
    url(r'aggregate-category-data', views.aggregate_category_data,
        name='aggregate_category_data'),
    url(r'get-uncategorized-images', views.get_uncategorized_photos,
        name='get_uncategorized_images')
]