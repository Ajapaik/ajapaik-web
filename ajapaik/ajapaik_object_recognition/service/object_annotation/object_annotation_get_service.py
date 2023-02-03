from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Profile
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, \
    FaceRecognitionRectangleSubjectDataSuggestion
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.detection_rectangle import DetectionRectangle
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass


def get_object_annotation_classes():
    object_classes = ObjectAnnotationClass.objects.all()
    return list(map(lambda x: {'label': x.translations, 'id': x.id}, object_classes))


def get_all_annotations(user_id, photo_id=None):
    photo = Photo.objects.get(pk=int(photo_id))

    object_rectangles = ObjectDetectionAnnotation.objects \
        .prefetch_related('feedback') \
        .filter(photo=photo, deleted_on__isnull=True)

    face_rectangles = FaceRecognitionRectangle.objects \
        .prefetch_related('feedback', 'face_recognition_rectangle') \
        .filter(photo=photo, deleted__isnull=True)

    objects = object_annotation_utils.transform_annotation_queryset(
        object_rectangles,
        map_object_rectangle_to_rectangle,
        user_id
    )

    faces = object_annotation_utils.transform_annotation_queryset(
        face_rectangles,
        map_face_rectangle_to_rectangle,
        user_id
    )

    # None values must be excluded https://code.djangoproject.com/ticket/20024
    person_subject_ai_suggestion_ids = face_rectangles.exclude(subject_ai_suggestion_id=None).values_list(
        'subject_ai_suggestion_id', flat=True)
    person_subject_consensus_ids = face_rectangles.exclude(subject_consensus_id=None).values_list(
        'subject_consensus_id', flat=True)
    album_photos = AlbumPhoto.objects.filter(photo=photo).exclude(album_id__in=person_subject_ai_suggestion_ids) \
        .exclude(album_id__in=person_subject_consensus_ids).filter(album__atype=Album.PERSON).distinct('album')

    persons = object_annotation_utils.transform_annotation_queryset(
        album_photos,
        map_person_album_to_rectangle
    )
    return objects + faces + persons


def map_object_rectangle_to_rectangle(object_annotation: ObjectDetectionAnnotation, user_id: int):
    previous_feedback = object_annotation.feedback.filter(user_id=user_id).order_by('-created_on').first()
    previous_feedback_object = previous_feedback.alternative_object if previous_feedback is not None else None

    alternative_object_id = previous_feedback_object.wiki_data_id if previous_feedback_object is not None else None
    alternative_object_translations = previous_feedback_object.translations \
        if previous_feedback_object is not None \
        else None

    user = Profile.objects.filter(user_id=user_id).first()

    return DetectionRectangle({
        'id': object_annotation.id,
        'x1': object_annotation.x1,
        'y1': object_annotation.y1,
        'x2': object_annotation.x2,
        'y2': object_annotation.y2,
        'wiki_data_id': object_annotation.detected_object.wiki_data_id,
        'translations': object_annotation.detected_object.translations,
        'is_editable': object_annotation_utils.is_object_annotation_editable(
            user_id,
            object_annotation
        ),
        'is_added_by_current_user': user_id == object_annotation.user_id,
        'has_user_given_feedback': object_annotation.feedback.all().exists(),
        'previous_feedback': {
            'is_correct_object': previous_feedback.confirmation if previous_feedback is not None else None,
            'alternative_object_id': alternative_object_id,
            'alternative_object_translations': alternative_object_translations
        },
        'user': user and user.get_display_name
    })


def map_face_rectangle_to_rectangle(face_annotation: FaceRecognitionRectangle, user_id: int):
    subject = face_annotation.get_subject()

    coordinates = face_annotation.decode_coordinates()
    subject_id = subject.id if subject is not None else None

    additional_data = FaceRecognitionRectangleSubjectDataSuggestion.objects.filter(
        proposer_id=user_id,
        face_recognition_rectangle_id=face_annotation.id).all().order_by('-created').first()
    if additional_data is None:
        additional_data = FaceRecognitionRectangle.objects.filter(id=face_annotation.id).all().first()
    original_user_set_gender = additional_data.gender if additional_data is not None else None
    original_user_set_age = additional_data.age if additional_data is not None else None
    gender_and_age = face_annotation.face_recognition_rectangle \
        .filter(proposer_id=user_id) \
        .first()
    previous_user_feedback = face_annotation.feedback.filter(user_id=user_id).order_by('-created').first()

    alternative_subject = previous_user_feedback.alternative_subject if previous_user_feedback is not None else None

    is_agreeing_on_age = gender_and_age is None or gender_and_age.age is None and original_user_set_age is not None
    is_agreeing_on_gender = not gender_and_age or not gender_and_age.gender and original_user_set_gender

    user = Profile.objects.filter(user_id=user_id).first()

    return DetectionRectangle({
        'id': face_annotation.id,
        'x1': coordinates[3],
        'y1': coordinates[0],
        'x2': coordinates[1],
        'y2': coordinates[2],
        'subject_id': subject_id,
        'subject_name': face_annotation.get_subject_name(),
        'is_editable': object_annotation_utils.is_face_annotation_editable(
            user_id,
            face_annotation
        ),
        'is_added_by_current_user': user_id == face_annotation.user_id,
        'gender': object_annotation_utils.parse_gender_to_constant(original_user_set_gender),
        'age': object_annotation_utils.parse_age_to_constant(original_user_set_age),
        'has_user_given_feedback': face_annotation.feedback.all().exists(),
        'previous_feedback': {
            'is_face': previous_user_feedback.is_correct if previous_user_feedback is not None else None,
            'is_correct_name': previous_user_feedback.is_correct_person if previous_user_feedback is not None else None,
            'subject_id': alternative_subject.id if alternative_subject is not None else None,
            'subject_name': alternative_subject.name if alternative_subject is not None else None,
            'is_correct_age': is_agreeing_on_age,
            'age': gender_and_age.age if gender_and_age is not None else None,
            'is_correct_gender': is_agreeing_on_gender,
            'gender': gender_and_age.gender if gender_and_age is not None else None
        },
        'user': user and user.get_display_name
    })


def map_person_album_to_rectangle(album_photo: AlbumPhoto):
    user = album_photo.profile

    return DetectionRectangle({
        'id': None,
        'x1': None,
        'y1': None,
        'x2': None,
        'y2': None,
        'subject_id': album_photo.album_id,
        'subject_name': album_photo.album.name,
        'is_editable': False,
        'is_added_by_current_user': False,
        'gender': object_annotation_utils.parse_gender_to_constant(album_photo.album.gender),
        'age': None,
        'has_user_given_feedback': False,
        'previous_feedback': {
            'is_face': None,
            'is_correct_name': None,
            'subject_id': None,
            'subject_name': None,
            'is_correct_age': None,
            'age': None,
            'is_correct_gender': None,
            'gender': None
        },
        user: user
    })
