import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo

class Command(BaseCommand):
    help = 'Calculate perceptual hash for images and then find similar images from all added images'

    def handle(self, *args, **options):
        photos =  Photo.objects.all()
        for photo in photos:
            try:
                photo.find_similar_for_existing_photo()
            except Exception:
                continue
