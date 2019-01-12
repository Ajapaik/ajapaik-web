from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will run set_calculated_fields and save for one or every photo"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
        except IndexError:
            photo_id = None
        if photo_id:
            photo = Photo.objects.get(pk=photo_id)
            photo.set_calculated_fields()
            photo.save()
        else:
            for photo in Photo.objects.filter(rephoto_of__isnull=True):
                #print photo
                photo.set_calculated_fields()
                photo.save()