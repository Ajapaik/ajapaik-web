# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Will try to reverse geocode all photos'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        for p in photos:
            p.reverse_geocode_location()
            p.light_save()
