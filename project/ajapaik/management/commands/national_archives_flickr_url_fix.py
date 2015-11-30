from django.core.management import BaseCommand

from project.ajapaik.models import Album, Licence


class Command(BaseCommand):
    help = "Will fix National Archives URLs"

    def handle(self, *args, **options):
        a = Album.objects.get(pk=3075)
        photos = a.photos.all()
        licence = Licence.objects.get(pk=8)
        for p in photos:
            p.source_url = p.source_url.replace(' ', '_')
            p.licence = licence
            p.light_save()