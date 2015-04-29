from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will autopopulate width/height fields for photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(height__isnull=True)
        for p in photos:
            print p.id
            p.save()