from ajapaik.ajapaik_object_recognition.domain.object_annotation_update_request import ObjectAnnotationUpdateRequest
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass


def update_object_annotation(request: ObjectAnnotationUpdateRequest):
    annotation = ObjectDetectionAnnotation.objects.get(pk=request.rectangle_id)
    detection_class = ObjectAnnotationClass.objects.get(pk=request.alternative_object_id)

    annotation.detected_object = detection_class

    annotation.save()
