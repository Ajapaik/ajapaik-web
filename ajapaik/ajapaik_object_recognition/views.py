import logging

from django.http import HttpResponse, HttpRequest, QueryDict

from ajapaik.ajapaik_object_recognition import response
from ajapaik.ajapaik_object_recognition.domain.add_detection_annotation import AddDetectionAnnotation
from ajapaik.ajapaik_object_recognition.domain.add_object_detection_feedback import AddObjectDetectionFeedback
from ajapaik.ajapaik_object_recognition.domain.annotation_remove_request import AnnotationRemove
from ajapaik.ajapaik_object_recognition.domain.object_annotation_update_request import ObjectAnnotationUpdateRequest
from ajapaik.ajapaik_object_recognition.domain.remove_object_annotation_feedback import RemoveObjectAnnotationFeedback
from ajapaik.ajapaik_object_recognition.service.object_annotation import object_annotation_modify_service, \
    object_annotation_add_service, object_annotation_get_service, object_annotation_delete_service
from ajapaik.ajapaik_object_recognition.service.object_feedback import object_annotation_feedback_service


log = logging.getLogger(__name__)


def add_annotation(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return response.not_supported()

    add_detection_annotation = AddDetectionAnnotation(QueryDict(request.body), request.user.id)

    object_annotation_add_service.add_annotation(add_detection_annotation, request)

    return response.success()


def update_annotation(request: HttpRequest) -> HttpResponse:
    if request.method != 'PUT':
        return response.not_supported()

    object_annotation_update_request = ObjectAnnotationUpdateRequest(QueryDict(request.body))

    object_annotation_modify_service.update_object_annotation(object_annotation_update_request)

    return response.success()


def remove_annotation(request: HttpRequest, annotation_id: int) -> HttpResponse:
    if request.method != 'DELETE':
        return response.not_supported()

    annotation_remove_request = AnnotationRemove(annotation_id, request.user.id)

    has_deleted_successfully = object_annotation_delete_service.remove_annotation(annotation_remove_request)

    if has_deleted_successfully:
        return response.success()
    else:
        return response.action_failed()


def get_all_annotations(request, photo_id=None) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    all_rectangles = object_annotation_get_service.get_all_annotations(request.user.id, photo_id)

    return response.success(all_rectangles)


def get_object_annotation_classes(request: HttpRequest) -> HttpResponse:
    if request.method != 'GET':
        return response.not_supported()

    response_data = object_annotation_get_service.get_object_annotation_classes()

    return response.success(response_data)


def add_feedback(request, annotation_id):
    if request.method == 'POST':
        add_object_detection_feedback = AddObjectDetectionFeedback(
            QueryDict(request.body),
            request.user.id,
            annotation_id
        )

        object_annotation_feedback_service.add_feedback(add_object_detection_feedback)

        return response.success()
    elif request.method == 'DELETE':
        remove_object_annotation_feedback = RemoveObjectAnnotationFeedback(annotation_id, request.user.id)
        object_annotation_feedback_service.remove_feedback(remove_object_annotation_feedback)

        return response.success()

    return response.not_supported()

