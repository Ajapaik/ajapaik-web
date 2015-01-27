from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will run set_calculated_fields for every photo"
    args = "photo_id"

    def handle(self, *args, **options):
        photo_id = args[0]
        if photo_id:
            Photo.objects.get(pk=photo_id).set_calculated_fields().save()
        else:
            for photo in Photo.objects.all():
                print photo.id
                photo.set_calculated_fields()
                photo.save()