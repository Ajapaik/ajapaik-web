# coding=utf-8
from ajapaik.ajapaik.api import AjapaikAPIView
from ajapaik.ajapaik.models import Profile
from ajapaik.ajapaik_face_recognition.domain.add_additional_subject_data import AddAdditionalSubjectData
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class AddSubjectData(AjapaikAPIView):
    '''
    API endpoint for posting subject data.
    '''
    def post(self, request, format=None):
        subject_id = request.POST.get('subjectId', None)
        age = request.POST.get('age', None)
        gender = request.POST.get('gender', None)

        additional_subject_data = AddAdditionalSubjectData(subject_rectangle_id=subject_id, age=age, gender=gender)

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
        age = additional_subject_data.age
        gender = additional_subject_data.gender
        gender2 = gender

        if gender == 2:
            gender2 = None
        if subject_annotation_rectangle_id is not None:
            subject = get_object_or_404(FaceRecognitionRectangle, id=subject_annotation_rectangle_id)
            if subject is None:
                return JsonResponse({'status': 400})
            points += FaceRecognitionRectangle.add_subject_data(subject, profile, age, gender2)

        return JsonResponse({'points': points})
