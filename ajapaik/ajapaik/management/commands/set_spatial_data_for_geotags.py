from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import GeoTag


class Command(BaseCommand):
    help = "Set geography field for geotags"
    args = "photo_id"

    def handle(self, *args, **options):
        try:
            photo_id = args[0]
        except IndexError:
            photo_id = None
        geotags = GeoTag.objects.all()
        if photo_id:
            geotags = geotags.filter(photo_id=photo_id)
        for g in geotags:
            g.save()
