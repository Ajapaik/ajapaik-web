from django.core.management.base import BaseCommand
from project.sift.models import CatPhoto


class Command(BaseCommand):
    help = 'Extract muis_id from URL'

    def handle(self, *args, **options):
        photos = CatPhoto.objects.filter(source_url__icontains='muis.ee')
        for p in photos:
            p.muis_id = p.source_url.split('/')[-1]
            p.save()
