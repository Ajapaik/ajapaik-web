from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik_face_recognition.domain.face_annotation_update_request import FaceAnnotationUpdateRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionUserGuess
from ajapaik.ajapaik_object_recognition import object_annotation_utils


def update_face_annotation(request: FaceAnnotationUpdateRequest) -> bool:
    annotation = FaceRecognitionRectangle.objects.get(
        pk=request.annotation_id,
        user_id=request.user_id
    )

    is_annotation_editable = object_annotation_utils.is_annotation_deletable(
        request.user_id,
        annotation.created,
        annotation.user_id
    )

    if not is_annotation_editable:
        return False

    if request.new_subject_id > 0:
        new_subject = Album.objects.get(pk=request.new_subject_id)
        annotation.subject_consensus = new_subject

        user_guess = get_existing_user_guess(annotation, request)

        if user_guess is not None:
            user_guess.subject_album = new_subject
            user_guess.save()

    annotation.save()

    return True


def get_existing_user_guess(annotation: FaceRecognitionRectangle, request: FaceAnnotationUpdateRequest):
    try:
        return FaceRecognitionUserGuess.objects.get(
            rectangle=annotation,
            user_id=request.user_id
        )
    except FaceRecognitionUserGuess.DoesNotExist:
        return None
