import os
from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = 'Deletes photo files no longer needed from disk'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for p in photos:
            try:
                if p.image.file:
                    pass
            except IOError:
                print p.id