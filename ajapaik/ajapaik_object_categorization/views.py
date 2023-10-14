from django.views.decorators.csrf import csrf_exempt

from ajapaik.ajapaik.models import PhotoModelSuggestionAlternativeCategory
from ajapaik.ajapaik_object_categorization.service.object_categorization import object_categorization_service
from ajapaik.ajapaik_object_recognition import response
from django.http import HttpResponse, HttpRequest


def get_latest_category_from_result_table(request, photo_id=None) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    response_data = object_categorization_service.get_latest_category_from_result_table(photo_id)

    return response.success(response_data)


def get_uncategorized_photos(request: HttpRequest) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    response_data = object_categorization_service.get_uncategorized_photos()

    return response.success(response_data)


def propose_alternative_category(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return response.not_supported()
    alternative = PhotoModelSuggestionAlternativeCategory()

    alternative.viewpoint_elevation_alternation = request.POST.get("viewpoint_elevation_to_alternate", None)
    alternative.scene_alternation = request.POST.get("scene_to_alternate", None)
    alternative.photo_id = request.POST.get("photo_id", None)
    alternative.proposer = request.user.profile
    alternative.save()

    return response.success()

@csrf_exempt
def post_image_category_result_table(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return response.not_supported()

    object_categorization_service.post_image_category_result_table(request)

    return response.success()


def aggregate_category_data(request: HttpRequest) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    response_data = object_categorization_service.aggregate_category_data()

    return response.success(response_data)