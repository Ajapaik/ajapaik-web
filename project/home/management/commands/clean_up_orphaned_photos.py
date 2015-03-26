import os
from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = 'Deletes photo files no longer needed from disk'

    # TODO: Finish this, but very carefully as all photos are in the same folder
    # (staging, live, original, rephoto, scaled, unscaled etc)
    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for p in photos:
            path = '/var/garage/' + p.image.name
            if not os.path.isfile(path):
                print p.id