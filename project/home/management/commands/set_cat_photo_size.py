from django.core.management.base import BaseCommand
from project.home.models import CatPhoto


class Command(BaseCommand):
    help = "Will autopopulate width/height fields for Sift pics photos"

    def handle(self, *args, **options):
        photos = CatPhoto.objects.filter(height__isnull=True)
        for p in photos:
            print p.id
            p.save()