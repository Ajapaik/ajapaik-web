from django.http import HttpRequest

from ajapaik.ajapaik.models import Album, Photo, Profile
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_face_recognition.views import save_subject_object, add_person_rectangle
from ajapaik.ajapaik_object_recognition.domain.add_detection_annotation import AddDetectionAnnotation
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation, ObjectAnnotationClass


def add_annotation(add_detection_annotation: AddDetectionAnnotation, request: HttpRequest):
    object_id = add_detection_annotation.object_id
    subject_id = add_detection_annotation.subject_id

    photo_id = add_detection_annotation.photo_id

    if object_id is not None and object_id > 0:
        save_new_object_annotation(add_detection_annotation)
    else:
        photo = Photo.objects.get(pk=photo_id)
        new_face_annotation_id = add_person_rectangle(request.POST.copy(), photo, request.user.id)

        if subject_id is not None and subject_id > 0:
            save_detected_face(new_face_annotation_id, subject_id, request.user.id, request.user.profile)


def save_detected_face(new_rectangle_id, person_id, user_id, user_profile):
    new_rectangle = FaceRecognitionRectangle.objects.get(pk=new_rectangle_id)
    person_album = Album.objects.get(pk=person_id)

    save_subject_object(person_album, new_rectangle, user_id, user_profile)


def save_new_object_annotation(add_detection_annotation: AddDetectionAnnotation):
    object_id = add_detection_annotation.object_id
    photo_id = add_detection_annotation.photo_id
    user_id = add_detection_annotation.user_id

    x1 = add_detection_annotation.x1
    x2 = add_detection_annotation.x2
    y1 = add_detection_annotation.y1
    y2 = add_detection_annotation.y2

    new_annotation = ObjectDetectionAnnotation()

    new_annotation.photo = Photo.objects.get(pk=photo_id)

    new_annotation.x1 = x1
    new_annotation.x2 = x2
    new_annotation.y1 = y1
    new_annotation.y2 = y2
    new_annotation.detected_object = ObjectAnnotationClass.objects.get(pk=object_id)
    new_annotation.is_manual_detection = True

    new_annotation.user = Profile.objects.get(pk=user_id)

    new_annotation.save()
