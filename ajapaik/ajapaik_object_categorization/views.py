from ajapaik.ajapaik_object_categorization.service.object_categorization import object_categorization_get_service
from ajapaik.ajapaik_object_categorization import response
from django.http import HttpResponse


def get_latest_category(request, photo_id=None) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()
    print("I AM HERE")

    response_data = object_categorization_get_service.get_latest_category(photo_id)

    return response.success(response_data)
