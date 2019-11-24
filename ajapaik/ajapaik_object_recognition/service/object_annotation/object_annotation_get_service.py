from ajapaik.ajapaik.models import Photo
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from ajapaik.ajapaik_object_recognition.domain.detection_rectangle import DetectionRectangle
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass


def get_object_annotation_classes():
    object_classes = ObjectAnnotationClass.objects.all()
    return list(map(lambda x: {'label': x.translations, 'id': x.id}, object_classes))


def get_all_annotations(user_id, photo_id=None):
    photo = Photo.objects.get(pk=int(photo_id))

    object_rectangles = ObjectDetectionAnnotation.objects\
        .prefetch_related('feedback')\
        .filter(photo=photo, deleted_on__isnull=True)

    face_rectangles = FaceRecognitionRectangle.objects\
        .prefetch_related('feedback', 'face_recognition_rectangle')\
        .filter(photo=photo, deleted__isnull=True)

    objects = object_annotation_utils.transform_annotation_queryset(
        user_id,
        object_rectangles,
        map_object_rectangle_to_rectangle
    )

    faces = object_annotation_utils.transform_annotation_queryset(
        user_id,
        face_rectangles,
        map_face_rectangle_to_rectangle
    )

    return objects + faces


def map_object_rectangle_to_rectangle(object_annotation: ObjectDetectionAnnotation, user_id: int):
    return DetectionRectangle({
        'x1': object_annotation.x1,
        'y1': object_annotation.y1,
        'x2': object_annotation.x2,
        'y2': object_annotation.y2,
        'id': object_annotation.id,
        'wiki_data_id': object_annotation.detected_object.wiki_data_id,
        'translations': object_annotation.detected_object.translations,
        'is_deletable': object_annotation_utils.is_annotation_deletable(
            user_id,
            object_annotation.created_on,
            object_annotation.user.id
        ),
        'is_added_by_current_user': user_id == object_annotation.user.id,
        'has_user_given_feedback': object_annotation.feedback.all().count() > 0
    })


def map_face_rectangle_to_rectangle(face_annotation: FaceRecognitionRectangle, user_id: int):
    subject = face_annotation.get_subject()

    coordinates = face_annotation.decode_coordinates()
    subject_id = subject.id if subject is not None else None

    additional_data = face_annotation.face_recognition_rectangle.filter(guesser=face_annotation.user).first()
    original_user_set_gender = additional_data.gender if additional_data is not None else None
    original_user_set_age = additional_data.age if additional_data is not None else None

    return DetectionRectangle({
        'x1': coordinates[3],
        'y1': coordinates[0],
        'x2': coordinates[1],
        'y2': coordinates[2],
        'id': face_annotation.id,
        'subject_id': subject_id,
        'subject_name': face_annotation.get_subject_name(),
        'is_deletable': object_annotation_utils.is_annotation_deletable(
            user_id,
            face_annotation.created,
            face_annotation.user.id
        ),
        'is_added_by_current_user': user_id == face_annotation.user.id,
        'gender': object_annotation_utils.parse_gender_to_constant(original_user_set_gender),
        'age': object_annotation_utils.parse_age_to_constant(original_user_set_age),
        'has_user_given_feedback': face_annotation.feedback.all().count() > 0
    })
