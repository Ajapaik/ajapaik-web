from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.object_annotation_update_request import ObjectAnnotationUpdateRequest
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation
from ajapaik.ajapaik_object_recognition.service.object_annotation import object_annotation_common_service


def update_object_annotation(user_id: int, request: ObjectAnnotationUpdateRequest):
    if request.wiki_data_label_id is None:
        raise Exception('Object ID must be provided')

    annotation = ObjectDetectionAnnotation.objects.get(pk=request.rectangle_id)

    if not object_annotation_utils.is_object_annotation_editable(user_id, annotation):
        return False

    detection_class = object_annotation_common_service.get_saved_label(request.wiki_data_label_id)

    annotation.detected_object = detection_class

    annotation.save()
