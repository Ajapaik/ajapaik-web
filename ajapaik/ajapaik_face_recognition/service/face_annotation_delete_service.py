from datetime import date

from ajapaik.ajapaik.models import AlbumPhoto
from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle


def remove_annotation(annotation_remove_request: FaceAnnotationRemoveRequest) -> bool:
    face_detection_annotation = FaceRecognitionRectangle.objects.get(
        pk=annotation_remove_request.annotation_id
    )

    photo = face_detection_annotation.photo
    consensus = face_detection_annotation.subject_consensus
    if (consensus and not FaceRecognitionRectangle.objects.filter(photo=photo, subject_consensus=consensus).exclude(
            id=face_detection_annotation.id).exclude(deleted__isnull=False).exists()):
        album_photos = AlbumPhoto.objects.filter(photo=photo, album=consensus)
        for ap in album_photos:
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
