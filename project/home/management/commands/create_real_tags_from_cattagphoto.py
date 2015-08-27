from django.core.management.base import BaseCommand
from project.home.models import CatTag, CatRealTag


class Command(BaseCommand):
    help = "Will fill catrealtag from cattag"

    def handle(self, *args, **options):
        tags = CatTag.objects.all()
        for t in tags:
            parts = t.name.split('_')
            CatRealTag(
                name=parts[0]
            ).save()
            CatRealTag(
                name=t.name + '_NA'
            ).save()
            CatRealTag(
                name=parts[-1]
            ).save()