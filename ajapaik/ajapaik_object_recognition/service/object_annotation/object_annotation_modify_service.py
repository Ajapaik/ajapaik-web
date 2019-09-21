from ajapaik.ajapaik_object_recognition.domain.object_annotation_update_request import ObjectAnnotationUpdateRequest
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation
from ajapaik.ajapaik_object_recognition.service.object_annotation import object_annotation_common_service


def update_object_annotation(request: ObjectAnnotationUpdateRequest):
    annotation = ObjectDetectionAnnotation.objects.get(pk=request.rectangle_id)
    detection_class = object_annotation_common_service.get_saved_label(request.wiki_data_label_id)

    annotation.detected_object = detection_class

    annotation.save()
