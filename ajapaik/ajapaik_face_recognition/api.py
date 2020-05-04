# coding=utf-8
from ajapaik.ajapaik.api import AjapaikAPIView
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo, Profile
from ajapaik.ajapaik_face_recognition.domain.add_additional_subject_data import AddAdditionalSubjectData
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from ajapaik.ajapaik_object_recognition import object_annotation_utils
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


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
        if newSubjectId is not None and newSubjectId is not '':
            person_album = Album.objects.get(pk=newSubjectId)
        new_rectangle = FaceRecognitionRectangle.objects.get(pk=annotation_id)
        if(person_album and len(AlbumPhoto.objects.filter(photo=new_rectangle.photo,album=person_album)) < 1):
            albumPhoto = AlbumPhoto(album=person_album, photo=new_rectangle.photo, type=AlbumPhoto.FACE_TAGGED, profile=request.user.profile)
            albumPhoto.save()
            person_album.set_calculated_fields()
            person_album.save()

        additional_subject_data = AddAdditionalSubjectData(subject_rectangle_id=annotation_id, age=age, gender=gender, newSubjectId=newSubjectId)

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
        gender2 = gender

        if gender == 'NON-BINARY':
            gender2 = None
        if subject_annotation_rectangle_id is not None:
            subject = get_object_or_404(FaceRecognitionRectangle, id=subject_annotation_rectangle_id)
            if new_subject_id is not None:
                subject.subject_consensus = Album.objects.filter(id=new_subject_id).first()
                subject.save()
            if subject is None:
                return JsonResponse({'status': 400})
            points += FaceRecognitionRectangle.add_subject_data(subject, profile, age, gender2)

        return JsonResponse({'points': points})

class AlbumData(AjapaikAPIView):
    '''
    API Endpoint to check if album has face annotations
    '''
    @staticmethod
    def get(request, album_id):
        if Album.objects.filter(id=album_id) is None:
            return JsonResponse({'Album does not exist'})
        albumPhotoIds = AlbumPhoto.objects.filter(album_id=album_id).values_list('photo_id', flat=True)
        return JsonResponse({'hasAnnotations': FaceRecognitionRectangle.objects.filter(deleted=None, photo_id__in=albumPhotoIds).count() > 0})