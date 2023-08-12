import json

from django.db.models import Max
from django.http import HttpRequest

from ajapaik.ajapaik.models import PhotoSceneSuggestion, PhotoViewpointElevationSuggestion, \
    PhotoModelSuggestionConfirmReject, Photo, PhotoModelSuggestionResult, PhotoModelSuggestionAlternativeCategory
from django.core import serializers
import datetime


def get_latest_category_from_result_table(photo_id=None):
    result = PhotoModelSuggestionResult.objects.filter(photo_id=photo_id).order_by('-created')
    result_categories = []

    print("RESULT IS")


    if result.exists():
        categories = serializers.serialize('python', [result.first()])
        print(categories)
        result_categories.append(categories[0])

    return result_categories


def confirm_photo_category(photo_id=None):
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


def get_uncategorized_photos():
    """
    Method returns uncategorized photos for further category prediction.
    Uncategorized images are those that are:
       - not present in original Photo table
       - are not present in PhotoModelSuggestionResult (meaning to category was computed for them before)
    """

    photos = Photo.objects.filter(scene=None, viewpoint_elevation=None).values_list('id', 'user', 'image')

    photos_without_results = []
    for photo in photos:
        if not PhotoModelSuggestionResult.objects.filter(photo_id=photo[0]).exists():
            photos_without_results.append(photo)

    return photos_without_results


def confirm_reject_category(request: HttpRequest):
    suggestion = PhotoModelSuggestionConfirmReject()

    suggestion.viewpoint_elevation_to_confirm = request.POST.get("viewpoint_elevation_to_confirm", None)
    suggestion.scene_to_confirm = request.POST.get("scene_to_confirm", None)
    suggestion.viewpoint_elevation_to_reject = request.POST.get("viewpoint_elevation_to_reject", None)
    suggestion.scene_to_reject = request.POST.get("scene_to_reject", None)
    suggestion.photo_id = request.POST.get("photo_id", None)
    suggestion.proposer = request.user.profile  # assuming you have a user profile model and the user is authenticated

    suggestion.save()
    return suggestion


def post_image_category_result_table(request: HttpRequest):
    result = PhotoModelSuggestionResult()
    data = json.loads(request.body)

    result.viewpoint_elevation = data.get("verdict_view_point_elevation", None)
    result.scene = data.get("verdict_scene", None)
    result.photo_id = data.get("photo_id", None)
    result.save()
    return result


# def aggregate_category_data():
#     """
#     Methods aggregates data from both Alternative table + User's categories input.
#     """
#
#     one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
#
#     # scene_category = PhotoSceneSuggestion.objects.filter(created__gte=one_week_ago).order_by('-created')
#     # view_point_category = PhotoViewpointElevationSuggestion.objects.filter(created__gte=one_week_ago).order_by(
#     #     '-created')
#
#     alternative_category = PhotoModelSuggestionAlternativeCategory.objects.filter(created__gte=one_week_ago).order_by(
#         '-created')
#
#     result_categories = {}
#
#     # if scene_category.exists():
#     #     scene_category_dict = serializers.serialize('python', scene_category)
#     #     result_categories['scene_category_data'] = scene_category_dict
#     #
#     # if view_point_category.exists():
#     #     view_point_dict = serializers.serialize('python', view_point_category)
#     #     result_categories['view_point_category_data'] = view_point_dict
#
#     if alternative_category.exists():
#         confirm_reject_dict = serializers.serialize('python', alternative_category)
#         result_categories['alternative_category_data'] = confirm_reject_dict
#
#     return result_categories

def aggregate_category_data():
    """
    Method aggregates data from both Alternative table + User's categories input.
    """

    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    # scene_category = PhotoSceneSuggestion.objects.filter(created__gte=one_week_ago).order_by('-created')
    # view_point_category = PhotoViewpointElevationSuggestion.objects.filter(created__gte=one_week_ago).order_by(
    #     '-created')

    alternative_category = PhotoModelSuggestionAlternativeCategory.objects.filter(created__gte=one_week_ago).order_by(
        '-created')

    result_categories = {}

    # if scene_category.exists():
    #     scene_category_dict = serializers.serialize('python', scene_category)
    #     result_categories['scene_category_data'] = scene_category_dict
    #
    # if view_point_category.exists():
    #     view_point_dict = serializers.serialize('python', view_point_category)
    #     result_categories['view_point_category_data'] = view_point_dict

    if alternative_category.exists():
        confirm_reject_dict = serializers.serialize('python', alternative_category)
        result_categories['alternative_category_data'] = confirm_reject_dict

    print("=====")
    print(result_categories)
    return result_categories


class UncategorizedPhoto:
    def __init__(self, image_id, user_id, image_name):
        self.image_id = image_id
        self.user_id = user_id
        self.image_name = image_name