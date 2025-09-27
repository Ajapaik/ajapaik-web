import json

from django.http import HttpRequest

from ajapaik.ajapaik.models import Photo, PhotoModelSuggestionResult, \
    PhotoModelSuggestionAlternativeCategory
from django.core import serializers
import datetime


def get_latest_category_from_result_table(photo_id=None):
    result = PhotoModelSuggestionResult.objects.filter(photo_id=photo_id).order_by('-created')

    if result.exists():
        categories = serializers.serialize('python', result)
        return categories
    return []


def get_uncategorized_photos():
    photos = Photo.objects.filter(scene=None, viewpoint_elevation=None).values_list('id', 'user', 'image')

    photos_without_results = []
    for photo in photos:
        if not PhotoModelSuggestionResult.objects.filter(photo_id=photo[0]).exists():
            photos_without_results.append(photo)

    return photos_without_results


def post_image_category_result_table(request: HttpRequest):
    result = PhotoModelSuggestionResult()
    data = json.loads(request.body)

    result.viewpoint_elevation = data.get("verdict_view_point_elevation", None)
    result.scene = data.get("verdict_scene", None)
    result.photo_id = data.get("photo_id", None)
    result.save()
    return result


def aggregate_category_data():
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    alternative_category = PhotoModelSuggestionAlternativeCategory.objects.filter(created__gte=one_week_ago).order_by(
        '-created')

    result_categories = {}

    if alternative_category.exists():
        confirm_reject_dict = serializers.serialize('python', alternative_category)
        result_categories['alternative_category_data'] = confirm_reject_dict

    return result_categories


class UncategorizedPhoto:
    def __init__(self, image_id, user_id, image_name):
        self.image_id = image_id
        self.user_id = user_id
        self.image_name = image_name
