from django.core.management.base import BaseCommand
from project.sift.models import CatPhoto


class Command(BaseCommand):
    help = 'Remove /portaal part from MUIS URL'

    def handle(self, *args, **options):
        photos = CatPhoto.objects.all()
        for p in photos:
            if 'portaal' in p.source_url:
                p.source_url = p.source_url.replace('/portaal', '')
                p.light_save()