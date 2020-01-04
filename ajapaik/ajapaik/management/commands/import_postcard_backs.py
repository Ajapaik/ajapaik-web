
from django.core.management.base import BaseCommand                                                                                                                                                                                                                       
from django.shortcuts import get_object_or_404
from ajapaik import settings
from ajapaik.ajapaik.models import Album, AlbumPhoto, Photo
import os

class Command(BaseCommand):
    help = 'Add photo objects for postcard backs in DIGAR'
    def handle(self, *args, **options):
        photos = os.listdir(settings.MEDIA_ROOT + "/uploads/Digar_postkaartide_tagakyljed/")
        for p in photos:
            first = Photo.objects.filter(external_id=p.split("_")[1]).first()
            if first is None or (first.source_url and not 'digar' in first.source_url):
                print(p.split("_")[1])
            else:
                new_photo = Photo(
                    image=settings.MEDIA_ROOT + "/uploads/Digar_postkaartide_tagakyljed/DIGAR_" + p.split("_")[1] + "_2.jpg",
                    source=first.source,
                    source_url=first.source_url,
                    source_key=first.source_key,
                    licence=first.licence,
                    description=first.description
                )
                if first.title:
                    new_photo.title = first.title
                if first.description:
                    new_photo.description = first.description
                if first.author:
                    new_photo.author = first.author
                if first.licence_id:
                    new_photo.licence_id = first.licence_id
                if first.source_id:
                    new_photo.source_id = first.source_id
                if first.source_url:
                    new_photo.source_url = first.source_url
                if first.source_key:
                    new_photo.source_key = first.source_key
                if first.date_text:
                    new_photo.date_text = first.date_text
                if first.date:
                    new_photo.date = first.date
                try:
                    new_photo.save()
                    first.set_postcard(new_photo)
                except Exception as e:
                    print(e)    