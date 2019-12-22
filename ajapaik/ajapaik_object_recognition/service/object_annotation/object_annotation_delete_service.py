from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.annotation_remove_request import AnnotationRemove
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


def remove_annotation(annotation_remove_request: AnnotationRemove) -> bool:
    user_id = annotation_remove_request.user_id

    object_detection_annotation = ObjectDetectionAnnotation.objects.get(
        pk=annotation_remove_request.annotation_id,
        user_id=user_id
    )

    is_deletable = object_annotation_utils.is_annotation_deletable(
        user_id,
        object_detection_annotation.created_on,
        object_detection_annotation.user
    )

    if is_deletable:
        object_detection_annotation.delete()
        return True

    return False
