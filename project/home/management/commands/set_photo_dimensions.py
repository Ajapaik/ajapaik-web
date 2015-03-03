from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will calculate photo dimensions for all photos, will delete photos without images"

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        for p in photos:
            try:
                print "Saving photo %d" % p.id
                p.save()
            except IOError as err:
                print "Deleting photo %d" % p.id
                p.delete()