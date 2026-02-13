from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Will run set_calculated_fields and save for one or every photo"
    args = "photo_id"

    def handle(self, *args, **options):
        photos=Photo.objects.filter(first_rephoto__isnull=False)
        print(photos.count())
        n=0
        m=0
        for photo in photos:
            n=n+1
            if (n>100):
                n=0
                m=m+1
                print(m)
            photo.rephoto_count=photo.rephotos.count()
            photo.light_save()
