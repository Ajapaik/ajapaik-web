import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.phash import phash
from ajapaik.models import Photo

class Command(BaseCommand):
    help = 'Calculate perceptual hash for images and then find similar images from all added images'

    def handle(self, *args, **options):
        newPhotos =  Photo.objects.filter(perceptual_hash__isnull)
        for newPhoto in newPhotos:
            newPhoto.find_similar()