# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Will try to reverse geocode all photos'

    def handle(self, *args, **options):
        start = 0
        end = 10000
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        count = photos.count()
        while end < count:
            for p in photos[start:end]:
                p.reverse_geocode_location()
                p.light_save()
            start += 10000
            end += 10000
