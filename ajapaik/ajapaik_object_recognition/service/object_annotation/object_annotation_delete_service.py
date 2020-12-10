from datetime import date

from ajapaik.ajapaik_object_recognition.domain.annotation_remove_request import AnnotationRemove
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


def remove_annotation(annotation_remove_request: AnnotationRemove) -> bool:
    object_detection_annotation = ObjectDetectionAnnotation.objects.get(
        pk=annotation_remove_request.annotation_id
    )

    object_detection_annotation.deleted_on = date.today()
    object_detection_annotation.save()

    if (object_detection_annotation.photo.annotation_count > 0):
        object_detection_annotation.photo.annotation_count -= 1
        if (object_detection_annotation.photo.annotation_count == 0):
            object_detection_annotation.photo.latest_annotation = None
            object_detection_annotation.photo.first_annotation = None
        object_detection_annotation.photo.light_save()

    return True
