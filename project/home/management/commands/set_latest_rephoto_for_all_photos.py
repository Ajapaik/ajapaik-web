from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Set latest rephoto for all photos"

    def handle(self, *args, **options):
        rephotos = Photo.objects.filter(rephoto_of__isnull=False)
        for rp in rephotos:
            print rp.id
            if rp.rephoto_of.latest_rephoto is None or rp.rephoto_of.latest_rephoto < rp.created:
                rp.rephoto_of.latest_rephoto = rp.created
                rp.rephoto_of.light_save()