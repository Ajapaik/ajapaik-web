"""
Application api endpoints.
"""
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from project.ajapaik.models import Photo

from . import serializers


class PhotoMassiveUpload(CreateAPIView):
    '''
    API endpoint to upload multiple photos from massive upload form.
    '''
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    serializer_class = serializers.PhotoSerializer
    queryset = Photo.objects.all()

    def perform_create(self, serializer):
        return
