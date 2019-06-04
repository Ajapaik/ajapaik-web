import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo

class Command(BaseCommand):
    help = 'Calculate perceptual hash for all images'

    def handle(self, *args, **options):
        photos =  Photo.objects.all().filter(perceptual_hash__isnull=True)
        for photo in photos:
            try:
                photo.calculate_phash()
            except Exception:
                continue
