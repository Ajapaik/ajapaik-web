from datetime import date

from ajapaik.ajapaik.models import AlbumPhoto
from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, \
    FaceRecognitionRectangleSubjectDataSuggestion


def remove_annotation(annotation_remove_request: FaceAnnotationRemoveRequest) -> bool:
    face_detection_annotation = FaceRecognitionRectangle.objects.get(
        pk=annotation_remove_request.annotation_id
    )

    photo = face_detection_annotation.photo
    consensus = face_detection_annotation.subject_consensus
    if (consensus and len(FaceRecognitionRectangle.objects.filter(photo=photo, subject_consensus=consensus).exclude(
            id=face_detection_annotation.id).exclude(deleted__isnull=False)) < 1):
        albumPhotos = AlbumPhoto.objects.filter(photo=photo, album=consensus)
        for ap in albumPhotos:
            ap.delete()
        consensus.set_calculated_fields()
        consensus.save()

    face_detection_annotation.deleted = date.today()
    face_detection_annotation.save()

    if (photo.annotation_count is not None and photo.annotation_count > 0):
        photo.annotation_count -= 1
        if (photo.annotation_count == 0):
            photo.first_annotation = None
            photo.latest_annotation = None

        photo.light_save()

    return True


def get_annotation_subject_data_suggestions(face_recognition_rectangle_id):
    return FaceRecognitionRectangleSubjectDataSuggestion.objects \
        .filter(face_recognition_rectangle_id=face_recognition_rectangle_id)
