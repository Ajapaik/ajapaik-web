from django.core.management.base import BaseCommand
from django.db.models import Count
from project.home.models import GeoTag, Photo


class Command(BaseCommand):
    help = "If a photo only has one geotag, set it correct"

    def handle(self, *args, **options):
        photos = Photo.objects.annotate(geotag_count=Count('geotags')).filter(rephoto_of__isnull=True, geotag_count=1).all()
        print "Photos detected: " + str(len(photos))
        for p in photos:
            print p
            geotag = GeoTag.objects.get(photo_id=p.id)
            geotag.is_correct = True
            geotag.save()
            p.set_calculated_fields()
            p.save()