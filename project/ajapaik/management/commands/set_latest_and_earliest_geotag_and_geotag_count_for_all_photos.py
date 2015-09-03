from django.core.management.base import BaseCommand
from project.ajapaik.models import Photo


class Command(BaseCommand):
    help = "Set latest and earliest geotag, geotag count for all photos"

    def handle(self, *args, **options):
        photos = Photo.bulk.filter(rephoto_of__isnull=True).prefetch_related('geotags')
        for p in photos:
            p.geotag_count = p.geotags.distinct('user_id').count()
            latest_geotag = p.geotags.order_by('-created').first()
            if latest_geotag:
                p.latest_geotag = latest_geotag.created
            earliest_geotag = p.geotags.order_by('-created').last()
            if earliest_geotag:
                p.first_geotag = earliest_geotag.created
        Photo.bulk.bulk_update(photos, update_fields=['first_geotag', 'latest_geotag', 'geotag_count'])