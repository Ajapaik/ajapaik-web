from django.http import HttpRequest

from ajapaik.ajapaik.models import Album
from ajapaik.ajapaik_face_recognition.api import AddSubjectData
from ajapaik.ajapaik_face_recognition.domain.add_additional_subject_data import AddAdditionalSubjectData
from ajapaik.ajapaik_face_recognition.domain.face_annotation_update_request import FaceAnnotationUpdateRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionUserGuess, \
    FaceRecognitionRectangleSubjectDataGuess
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.object_annotation_utils import AGE_NOT_SURE, GENDER_NOT_SURE


def update_face_annotation(request: FaceAnnotationUpdateRequest, http_request: HttpRequest) -> bool:
    annotation = FaceRecognitionRectangle.objects.get(
        pk=request.annotation_id,
        user_id=request.user_id
    )

    is_annotation_editable = object_annotation_utils.is_annotation_deletable(
        request.user_id,
        annotation.created,
        annotation.user
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

    update_user_guesses(http_request, annotation.id, request)
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


def update_user_guesses(http_request: HttpRequest, annotation_id: int, update_request: FaceAnnotationUpdateRequest):
    user_guess = get_existing_user_additional_data_guess(
        guesser=AddSubjectData.get_profile(http_request),
        annotation_id=annotation_id
    )

    has_age_guess = update_request.new_age_guess is not None and update_request.new_age_guess != AGE_NOT_SURE
    has_gender_guess = \
        update_request.new_gender_guess is not None and update_request.new_gender_guess != GENDER_NOT_SURE

    if user_guess is None and (has_age_guess or has_gender_guess):
        add_additional_subject_data = AddAdditionalSubjectData(
            subject_rectangle_id=annotation_id,
            age=update_request.new_age_guess,
            gender=update_request.new_gender_guess
        )
        AddSubjectData.add_subject_data(add_additional_subject_data, http_request)
    elif user_guess.gender != update_request.new_gender_guess or user_guess.age != update_request.new_age_guess:
        user_guess.age = update_request.new_age_guess
        user_guess.gender = update_request.new_gender_guess
        user_guess.save()


def get_existing_user_additional_data_guess(guesser, annotation_id):
    try:
        return FaceRecognitionRectangleSubjectDataGuess.objects.get(
            guesser=guesser,
            face_recognition_rectangle_id=annotation_id
        )
    except FaceRecognitionRectangleSubjectDataGuess.DoesNotExist:
        return None
