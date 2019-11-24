from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleSubjectDataGuess
from ajapaik.ajapaik_object_recognition import object_annotation_utils


def remove_annotation(annotation_remove_request: FaceAnnotationRemoveRequest) -> bool:
    user_id = annotation_remove_request.user_id

    face_detection_annotation = FaceRecognitionRectangle.objects.get(
        pk=annotation_remove_request.annotation_id,
        user_id=user_id
    )

    is_deletable = object_annotation_utils.is_annotation_deletable(
        user_id,
        face_detection_annotation.created,
        face_detection_annotation.user_id
    )

    if is_deletable:
        get_annotation_subject_data_guesses(face_detection_annotation.id).delete()
        face_detection_annotation.delete()
        return True

    return False


def get_annotation_subject_data_guesses(face_recognition_rectangle_id):
    return FaceRecognitionRectangleSubjectDataGuess.objects\
        .filter(face_recognition_rectangle_id=face_recognition_rectangle_id)
