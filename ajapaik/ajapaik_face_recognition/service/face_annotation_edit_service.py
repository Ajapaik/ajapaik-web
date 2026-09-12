from django.http import HttpRequest

from ajapaik.ajapaik.models import Album, Profile
from ajapaik.ajapaik_face_recognition.api import AddSubjectData
from ajapaik.ajapaik_face_recognition.domain.add_additional_subject_data import AddAdditionalSubjectData
from ajapaik.ajapaik_face_recognition.domain.face_annotation_update_request import FaceAnnotationUpdateRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionUserSuggestion, \
    FaceRecognitionRectangleSubjectDataSuggestion
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.object_annotation_utils import AGE_NOT_SURE, GENDER_NOT_SURE


def update_face_annotation(request: FaceAnnotationUpdateRequest, http_request: HttpRequest) -> bool:
    annotation: FaceRecognitionRectangle = FaceRecognitionRectangle.objects.get(pk=request.annotation_id)

    is_annotation_editable = object_annotation_utils.is_face_annotation_editable(
        user_id=request.user_id,
        annotation=annotation
    )

    if not is_annotation_editable:
        return create_user_feeback(annotation, request)
    else:
        if request.new_subject_id > 0:
            new_subject = Album.objects.get(pk=request.new_subject_id)
            annotation.subject_consensus = new_subject

            user_suggestion = get_existing_user_suggestion(annotation, request)

            if user_suggestion is not None:
                user_suggestion.subject_album = new_subject
                user_suggestion.save()

        if request.user_id == annotation.user_id:
            update_user_suggestions(http_request, annotation.id, request)

        annotation.save()

        if annotation.photo.first_annotation is None:
            annotation.photo.first_annotation = annotation.modified
        annotation.photo.latest_annotation = annotation.modified
        annotation.photo.light_save()

        return True


def get_existing_user_suggestion(annotation: FaceRecognitionRectangle, request: FaceAnnotationUpdateRequest):
    try:
        return FaceRecognitionUserSuggestion.objects.get(
            rectangle=annotation,
            id=request.user_id
        )
    except FaceRecognitionUserSuggestion.DoesNotExist:
        return None


def update_user_suggestions(http_request: HttpRequest, annotation_id: int, update_request: FaceAnnotationUpdateRequest):
    user_suggestion = get_existing_user_additional_data_suggestion(
        proposer=AddSubjectData.get_profile(http_request),
        annotation_id=annotation_id
    )

    has_age_suggestion = update_request.new_age_suggestion and update_request.new_age_suggestion != AGE_NOT_SURE
    has_gender_suggestion = \
        update_request.new_gender_suggestion is not None and update_request.new_gender_suggestion != GENDER_NOT_SURE

    if user_suggestion is None and (has_age_suggestion or has_gender_suggestion):
        add_additional_subject_data = AddAdditionalSubjectData(
            subject_rectangle_id=annotation_id,
            age=update_request.new_age_suggestion,
            gender=update_request.new_gender_suggestion
        )
        AddSubjectData.add_subject_data(add_additional_subject_data, http_request)
    elif user_suggestion.gender != update_request.new_gender_suggestion \
            or user_suggestion.age != update_request.new_age_suggestion:
        user_suggestion.age = update_request.new_age_suggestion
        user_suggestion.gender = update_request.new_gender_suggestion
        user_suggestion.save()


def create_user_feeback(annotation: FaceRecognitionRectangle, update_request: FaceAnnotationUpdateRequest):
    proposer = Profile.objects.filter(id=update_request.user_id).first()
    new_suggestion = FaceRecognitionRectangleSubjectDataSuggestion(face_recognition_rectangle=annotation,
                                                                   proposer=proposer,
                                                                   gender=update_request.new_gender_suggestion,
                                                                   age=update_request.new_age_suggestion)
    new_suggestion.save()
    return True


def get_existing_user_additional_data_suggestion(proposer, annotation_id):
    try:
        return FaceRecognitionRectangleSubjectDataSuggestion.objects.get(
            proposer=proposer,
            face_recognition_rectangle_id=annotation_id
        )
    except FaceRecognitionRectangleSubjectDataSuggestion.DoesNotExist:
        return None
