# coding=utf-8
from ajapaik.ajapaik.api import AjapaikAPIView
from ajapaik.ajapaik.models import Profile
from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import BasicAuthentication

class AddSubjectData(AjapaikAPIView):
    '''
    API endpoint for posting subject data.
    '''
    def post(self, request, format=None):
        points = 0
        errors = 0
        profile = None
        if request.user.is_anonymous:
            profile = request.POST.get('profile', None)
            profile = Profile.objects.filter(id=profile).first()
        else:
            profile = request.user.profile
        subjectId = request.POST.get('subjectId', None)
        age = request.POST.get('age', None)
        gender = request.POST.get('gender', None)
        gender2 = gender
        if gender == 2:
            gender2 = None
        if subjectId is not None:
            subject = get_object_or_404(FaceRecognitionRectangle, id=subjectId)
            if subject is None:
                return JsonResponse({'status': 400})
            points += FaceRecognitionRectangle.add_subject_data(subject, profile, age, gender2)
        return JsonResponse({'points': points})
