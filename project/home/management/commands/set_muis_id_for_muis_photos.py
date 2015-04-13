from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Set muis_id for photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(source_url__contains='muis.ee', muis_id__isnull=True).all()
        for p in photos:
            p.muis_id = "oai:muis.ee:" + p.source_url.split('/')[-1]
            p.save()