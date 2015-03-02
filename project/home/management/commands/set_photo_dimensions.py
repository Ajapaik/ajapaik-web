from django.core.management.base import BaseCommand
from project.home.models import Photo


class Command(BaseCommand):
    help = "Will calculate photo dimensions for all photos"

    def handle(self, *args, **options):
        photos = Photo.objects.all()
