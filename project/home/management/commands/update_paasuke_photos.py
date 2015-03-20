# coding=utf-8
from django.core.management.base import BaseCommand
from project.home.models import Album, CatPhoto, CatAlbum


class Command(BaseCommand):
    help = u"Set album for Pääsuke photos"

    def handle(self, *args, **options):
        album = CatAlbum.objects.get(pk=5)
        paasuke_photos = CatPhoto.filter(pk__gt=923).all()
        for each in paasuke_photos:
            album.photos.add(each)
        album.save()