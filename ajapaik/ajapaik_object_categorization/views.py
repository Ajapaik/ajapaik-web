from ajapaik.ajapaik.models import PhotoModelSuggestionConfirmReject
from ajapaik.ajapaik_object_categorization.service.object_categorization import object_categorization_service
from ajapaik.ajapaik_object_categorization import response
from django.http import HttpResponse, HttpRequest


def get_latest_category(request, photo_id=None) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    print("===")
    print(request)

    response_data = object_categorization_service.get_latest_category(photo_id)

    return response.success(response_data)


def confirm_latest_category(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return response.not_supported()
    suggestion = PhotoModelSuggestionConfirmReject()

    suggestion.viewpoint_elevation_to_confirm = request.POST.get("viewpoint_elevation_to_confirm", None)
    suggestion.scene_to_confirm = request.POST.get("scene_to_confirm", None)
    suggestion.viewpoint_elevation_to_reject = request.POST.get("viewpoint_elevation_to_reject", None)
    suggestion.scene_to_reject = request.POST.get("scene_to_reject", None)
    suggestion.photo_id = request.POST.get("photo_id", None)
    suggestion.proposer = request.user.profile  # assuming you have a user profile model and the user is authenticated

    # save the instance to the database
    suggestion.save()

    # redirect the user to a success page
    return response.success()

    # response_data = object_categorization_service.post_latest_category_confirmation(photo_id)
    #
    # return response.success(response_data)


def aggregate_category_data(request: HttpRequest) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    response_data = object_categorization_service.aggregate_category_data()

    return response.success(response_data)
