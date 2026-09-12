from django.urls import reverse
from rest_framework import serializers

from ajapaik.ajapaik.models import Photo
from ajapaik.utils import calculate_thumbnail_size


class PhotoMapMarkerSerializer(serializers.ModelSerializer):
    rephoto_count = serializers.IntegerField()

    url = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    is_selected = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.photo_selection = []
        if 'photo_selection' in kwargs:
            self.photo_selection = kwargs['photo_selection']
            # Django REST framework don't happy with unexpected parameters.
            del kwargs['photo_selection']
        super(PhotoMapMarkerSerializer, self).__init__(*args, **kwargs)

    def get_url(self, instance):
        return reverse(
            'image_thumb',
            args=(
                instance.id, 400, instance.get_pseudo_slug)
        )

    def get_permalink(self, instance):
        return reverse(
            'photo',
            args=(instance.id, instance.get_pseudo_slug)
        )

    def get_width(self, instance):
        return calculate_thumbnail_size(instance.width, instance.height, 400)[0]

    def get_height(self, instance):
        return calculate_thumbnail_size(instance.width, instance.height, 400)[1]

    def get_is_selected(self, instance):
        return str(instance.id) in self.photo_selection

    class Meta:
        model = Photo
        fields = (
            'id', 'lat', 'lon', 'azimuth', 'rephoto_count', 'description',
            'comment_count', 'url', 'permalink', 'width', 'height',
            'is_selected'
        )
