from random import randint
from django.core.management.base import BaseCommand
from django.db.models import Count
from project.home.models import Album


class Command(BaseCommand):
    help = "Refresh albums"

    def handle(self, *args, **options):
        albums = Album.objects.exclude(atype=Album.AUTO).annotate(photo_count=Count('photos'))
        for a in albums:
            if a.photo_count > 0:
                random_index = randint(0, a.photo_count - 1)
            else:
                random_index = 0
            try:
                a.cover_photo = a.photos.filter(rephoto_of__isnull=True)[random_index]
            except IndexError:
                for sa in a.subalbums.exclude(atype=Album.AUTO).annotate(photo_count=Count('photos')):
                    if sa.photo_count > 0:
                        random_index = randint(0, sa.photo_count - 1)
                        try:
                            a.cover_photo = sa.photos.filter(rephoto_of__isnull=True)[random_index]
                            break
                        except IndexError:
                            continue
            a.save()