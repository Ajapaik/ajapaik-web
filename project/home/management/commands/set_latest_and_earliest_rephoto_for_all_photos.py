from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Set latest and earliest rephoto for all photos"

    def handle(self, *args, **options):
        rephotos = Photo.bulk.filter(rephoto_of__isnull=False).prefetch_related('rephoto_of')
        for rp in rephotos:
            if rp.rephoto_of.latest_rephoto is None or rp.rephoto_of.latest_rephoto < rp.created:
                rp.rephoto_of.latest_rephoto = rp.created
                rp.latest_rephoto = None
            if rp.rephoto_of.first_rephoto is None or rp.rephoto_of.first_rephoto > rp.created:
                rp.rephoto_of.first_rephoto = rp.created
                rp.first_rephoto = None
        Photo.bulk.bulk_update(rephotos, update_fields=['first_rephoto', 'latest_rephoto', 'rephoto_of__first_rephoto', 'rephoto_of__latest_rephoto'])