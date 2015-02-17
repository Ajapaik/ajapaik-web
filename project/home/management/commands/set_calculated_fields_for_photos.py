from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will run set_calculated_fields for every photo"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
        except:
            photo_id = None
        if photo_id:
            photo = Photo.objects.get(pk=photo_id)
            photo.set_calculated_fields()
            photo.save()
        else:
            for photo in Photo.objects.all():
                photo.set_calculated_fields()
                photo.save()