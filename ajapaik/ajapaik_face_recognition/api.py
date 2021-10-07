# coding=utf-8
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ajapaik.ajapaik.api import AjapaikAPIView
from ajapaik.ajapaik.models import Album, AlbumPhoto, Profile
from ajapaik.ajapaik_face_recognition.domain.add_additional_subject_data import AddAdditionalSubjectData
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition import object_annotation_utils


class AddSubjectData(AjapaikAPIView):
    '''
    API endpoint for posting subject data.
    '''

    def post(self, request, format=None):
        annotation_id = request.POST.get('annotationId', None)
        age = request.POST.get('ageGroup', None)
        gender = request.POST.get('gender', None)
        newSubjectId = request.POST.get('newSubjectId', None)
        person_album = None
        if newSubjectId and newSubjectId != '':
            person_album = Album.objects.filter(pk=newSubjectId).first()
        new_rectangle = FaceRecognitionRectangle.objects.get(pk=annotation_id)
        if (person_album and not AlbumPhoto.objects.filter(photo=new_rectangle.photo, album=person_album).exists()):
            albumPhoto = AlbumPhoto(album=person_album, photo=new_rectangle.photo, type=AlbumPhoto.FACE_TAGGED,
                                    profile=request.user.profile)
            albumPhoto.save()
            person_album.set_calculated_fields()
            person_album.save()

        additional_subject_data = AddAdditionalSubjectData(subject_rectangle_id=annotation_id, age=age, gender=gender,
                                                           newSubjectId=newSubjectId)

        return self.add_subject_data(additional_subject_data=additional_subject_data, request=request)

    @staticmethod
    def get_profile(request):
        if request.user.is_anonymous:
            profile = request.POST.get('profile', None)
            return Profile.objects.filter(user_id=profile).first()
        else:
            return request.user.profile

    @staticmethod
    def add_subject_data(additional_subject_data: AddAdditionalSubjectData, request):
        points = 0

        profile = AddSubjectData.get_profile(request)
        subject_annotation_rectangle_id = additional_subject_data.subject_annotation_rectangle_id
        new_subject_id = object_annotation_utils.parse_parameter(additional_subject_data.newSubjectId)
        age = additional_subject_data.age
        gender = additional_subject_data.gender
        if subject_annotation_rectangle_id is not None:
            subject = get_object_or_404(FaceRecognitionRectangle, id=subject_annotation_rectangle_id)
            if new_subject_id is not None:
                subject.subject_consensus = Album.objects.filter(id=new_subject_id).first()
                subject.save()
            if subject is None:
                return JsonResponse({'status': 400})
            points += subject.add_subject_data(profile=profile, age=age, gender=gender)

        return JsonResponse({'points': points})


class AlbumData(AjapaikAPIView):
    '''
    API Endpoint to check if album has face annotations
    '''

    @staticmethod
    def get(request, album_id):
        album = get_object_or_404(Album, id=album_id)
        album_photo_ids = AlbumPhoto.objects.filter(album_id=album.id).values_list('photo_id', flat=True)

        return JsonResponse({'hasAnnotations': FaceRecognitionRectangle.objects
                            .filter(deleted=None, photo_id__in=album_photo_ids).exists()})


class Annotation(AjapaikAPIView):
    '''
    API Endpoint to get annotation data
    '''

    @staticmethod
    def get(request, annotation_id):
        annotation = get_object_or_404(FaceRecognitionRectangle, id=annotation_id)
        user_id = annotation.user_id or None
        user_name = Profile.objects.get(pk=user_id).get_display_name if user_id else None
        photo_count = Album.objects.get(id=annotation.subject_consensus.id).photo_count_with_subalbums \
            if annotation.subject_consensus \
            else None
        return JsonResponse(
                {
                    'id': annotation.id,
                    'user_id': user_id,
                    'user_name': user_name,
                    'photo_count': photo_count
                }
            )
