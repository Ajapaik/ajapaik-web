from datetime import date
from ajapaik.ajapaik.models import AlbumPhoto, Photo
from ajapaik.ajapaik_face_recognition.domain.face_annotation_remove_request import FaceAnnotationRemoveRequest
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle, FaceRecognitionRectangleSubjectDataGuess
from ajapaik.ajapaik_object_recognition import object_annotation_utils


def remove_annotation(annotation_remove_request: FaceAnnotationRemoveRequest) -> bool:
    user_id = annotation_remove_request.user_id

    face_detection_annotation = FaceRecognitionRectangle.objects.get(
        pk=annotation_remove_request.annotation_id
    )
    
    photo = face_detection_annotation.photo
    consensus = face_detection_annotation.subject_consensus
    if(consensus and len(FaceRecognitionRectangle.objects.filter(photo=photo, subject_consensus=consensus).exclude(id=face_detection_annotation.id).exclude(deleted__isnull=False)) < 1):
        albumPhotos = AlbumPhoto.objects.filter(photo=photo, album=consensus)
        for ap in albumPhotos:
            ap.delete()
        consensus.set_calculated_fields()
        consensus.save()

    face_detection_annotation.deleted = date.today()
    face_detection_annotation.save()

    return True


def get_annotation_subject_data_guesses(face_recognition_rectangle_id):
    return FaceRecognitionRectangleSubjectDataGuess.objects\
        .filter(face_recognition_rectangle_id=face_recognition_rectangle_id)
