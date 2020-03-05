from datetime import date
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.annotation_remove_request import AnnotationRemove
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


def remove_annotation(annotation_remove_request: AnnotationRemove) -> bool:
    user_id = annotation_remove_request.user_id

    object_detection_annotation = ObjectDetectionAnnotation.objects.get(
        pk=annotation_remove_request.annotation_id,
        user_id=user_id
    )

    object_detection_annotation.deleted_on = date.today()
    object_detection_annotation.save()

    return True