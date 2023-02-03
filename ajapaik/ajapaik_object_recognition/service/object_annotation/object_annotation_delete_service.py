from datetime import date

from ajapaik.ajapaik_object_recognition.domain.annotation_remove_request import AnnotationRemove
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


def remove_annotation(annotation_remove_request: AnnotationRemove) -> None:
    object_detection_annotation = ObjectDetectionAnnotation.objects.get(
        pk=annotation_remove_request.annotation_id
    )

    object_detection_annotation.deleted_on = date.today()
    object_detection_annotation.save(update_fields=['deleted_on'])

    photo = object_detection_annotation.photo
    if photo.annotation_count > 0:
        photo.annotation_count -= 1
        if photo.annotation_count == 0:
            photo.latest_annotation = None
            photo.first_annotation = None
            photo.light_save(update_fields=['annotation_count', 'first_annotation', 'latest_annotation'])

        photo.light_save(update_fields=['annotation_count'])
