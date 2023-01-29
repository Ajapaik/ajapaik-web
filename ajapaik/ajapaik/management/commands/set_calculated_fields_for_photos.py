from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will run set_calculated_fields and save for one or every photo"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
            photos = Photo.objects.filter(pk=photo_id)
        except IndexError:
            photos = Photo.objects.filter(rephoto_of__isnull=True)

        for photo in photos:
            photo.set_calculated_fields()
            photo.save()
