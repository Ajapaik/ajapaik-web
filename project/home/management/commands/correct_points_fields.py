from django.core.management.base import BaseCommand
from project.home.models import Points


class Command(BaseCommand):
    help = "Set proper foreign key data for Points objects"

    def handle(self, *args, **options):
        photos = Points.objects.all()
        for p in photos:
            if p.action == Points.GEOTAG:
                p.geotag_id = p.action_reference
            else:
                p.photo_id = p.action_reference