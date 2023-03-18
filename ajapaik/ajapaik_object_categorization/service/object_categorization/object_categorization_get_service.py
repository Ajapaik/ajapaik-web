from ajapaik.ajapaik.models import PhotoSceneSuggestion, PhotoViewpointElevationSuggestion
from django.core import serializers


def get_latest_category(photo_id=None):
    # TODO: should query from calculated result table
    scene_category = PhotoSceneSuggestion.objects.filter(photo_id=photo_id).order_by('-created')
    view_point_category = PhotoViewpointElevationSuggestion.objects.filter(photo_id=photo_id).order_by('-created')

    result_categories = []

    if scene_category.exists():
        scene_category_dict = serializers.serialize('python', [scene_category.first()])
        result_categories.append(scene_category_dict[0])

    if view_point_category.exists():
        view_point_dict = serializers.serialize('python', [view_point_category.first()])
        result_categories.append(view_point_dict[0])

    return result_categories
