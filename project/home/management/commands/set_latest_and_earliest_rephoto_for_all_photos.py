from django.core.management.base import BaseCommand
from django.db.models import Count
from project.home.models import Photo


class Command(BaseCommand):
    help = "Set latest and earliest rephoto for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True).prefetch_related('rephotos').annotate(rp_count=Count('rephotos')).filter(rp_count__gt=0)
        for p in photos:
            earliest = None
            latest = None
            for rp in p.rephotos.order_by('created'):
                if not earliest:
                    earliest = rp.created
                if not latest:
                    latest = rp.created
                if rp.created > latest:
                    latest = rp.created
            p.first_rephoto = earliest
            p.latest_rephoto = latest
        Photo.bulk.bulk_update(photos, update_fields=['first_rephoto', 'latest_rephoto'])