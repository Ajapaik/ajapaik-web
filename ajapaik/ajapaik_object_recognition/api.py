# coding=utf-8
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ajapaik.ajapaik.api import AjapaikAPIView
from ajapaik.ajapaik.models import Profile
from ajapaik.ajapaik_object_recognition.models import ObjectDetectionAnnotation


class Annotation(AjapaikAPIView):
    '''
    API Endpoint to get annotation data
    '''

    @staticmethod
    def get(request, annotation_id):
        annotation = get_object_or_404(ObjectDetectionAnnotation, id=annotation_id)
        user_id = annotation.user_id or None
        user_name = Profile.objects.get(pk=user_id).get_display_name if user_id else None
        return JsonResponse(
            {
                'id': annotation.id,
                'user_id': user_id,
                'user_name': user_name
            }
        )
