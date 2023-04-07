from ajapaik.ajapaik.models import PhotoSceneSuggestion, PhotoViewpointElevationSuggestion, \
    PhotoModelSuggestionConfirmReject
from django.core import serializers
import datetime


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


def post_latest_category_confirmation(photo_id=None):

    # proposer = request.user.profile
    scene_category = PhotoModelSuggestionConfirmReject.objects.filter(photo_id=photo_id).order_by('-created')
    view_point_category = PhotoViewpointElevationSuggestion.objects.filter(photo_id=photo_id).order_by('-created')

    result_categories = []

    if scene_category.exists():
        scene_category_dict = serializers.serialize('python', [scene_category.first()])
        result_categories.append(scene_category_dict[0])

    if view_point_category.exists():
        view_point_dict = serializers.serialize('python', [view_point_category.first()])
        result_categories.append(view_point_dict[0])

    return result_categories


def aggregate_category_data():
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=30)

    scene_category = PhotoSceneSuggestion.objects.filter(created__gte=one_week_ago).order_by('-created')
    view_point_category = PhotoViewpointElevationSuggestion.objects.filter(created__gte=one_week_ago).order_by(
        '-created')
    confirm_reject_category = PhotoModelSuggestionConfirmReject.objects.filter(created__gte=one_week_ago).order_by(
        '-created')

    result_categories = {}

    if scene_category.exists():
        scene_category_dict = serializers.serialize('python', scene_category)
        result_categories['scene_category'] = scene_category_dict

    if view_point_category.exists():
        view_point_dict = serializers.serialize('python', view_point_category)
        result_categories['view_point_category'] = view_point_dict

    if confirm_reject_category.exists():
        confirm_reject_dict = serializers.serialize('python', confirm_reject_category)
        result_categories['confirm_reject_data'] = confirm_reject_dict

    return result_categories
