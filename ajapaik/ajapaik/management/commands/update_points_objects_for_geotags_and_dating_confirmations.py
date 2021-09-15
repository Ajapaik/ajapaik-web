from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Points


class Command(BaseCommand):
    help = 'Sets photo field for GeoTag Points, DatingConfirmation Points'

    def handle(self, *args, **options):
        qs = Points.objects.filter(action=Points.GEOTAG, photo_id__isnull=True).prefetch_related('geotag__photo')
        for each in qs:
            each.photo = each.geotag.photo
        Points.bulk.bulk_update(qs, update_fields=['photo_id'])
