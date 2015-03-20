# coding=utf-8
from PIL import Image
from copy import deepcopy
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from project.home.models import Album, CatPhoto


class Command(BaseCommand):
    help = "Make a categorizer album from an existing album"

    def handle(self, *args, **options):
        album_photos = Album.objects.get(pk=307).photos.all()
        for each in album_photos:
            cp = CatPhoto(
                title=each.description,
                description=each.description,
                author=u'Johannes Pääsuke',
                source=each.source,
                source_url=each.source_url
            )
            cp.image = deepcopy(each.image)
            cp.save()