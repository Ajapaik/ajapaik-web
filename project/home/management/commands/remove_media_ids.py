# encoding: utf-8
from django.core.management.base import BaseCommand
from project.home.models import Photo

class Command(BaseCommand):
    help = 'Remove second part of two-part MUIS ID'

    def handle(self, *args, **options):
        photos = Photo.objects.filter(muis_id__isnull=False)
        for p in photos:
            parts = p.muis_id.split('_')
            p.muis_id = parts[0]
            if len(parts) > 1:
                p.muis_media_id = parts[1]
            p.light_save()