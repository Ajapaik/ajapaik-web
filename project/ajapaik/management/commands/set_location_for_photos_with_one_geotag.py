from django.core.management.base import BaseCommand
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = "If photo has just 1 geotag, use its coordinates"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True, geotag_count=1)
        for p in photos:
            print p.id
            p.geotags.update(is_correct=True)
            p.set_calculated_fields()
            p.save()
            p.user.set_calculated_fields()
            p.user.save()