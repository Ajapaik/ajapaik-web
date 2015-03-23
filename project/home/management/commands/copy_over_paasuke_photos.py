# coding=utf-8
from copy import deepcopy
from django.core.management.base import BaseCommand
from project.home.models import Album, CatPhoto


class Command(BaseCommand):
    help = "Update photos key"

    def handle(self, *args, **options):
        album_photos = Album.objects.get(pk=307).photos.all()
        for each in album_photos:
            cp = CatPhoto.objects.get(source_url=each.source_url)
            cp.source_key = each.source_key
            print cp
            cp.save()