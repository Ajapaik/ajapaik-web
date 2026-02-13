from django.core.management.base import BaseCommand
from ajapaik.ajapaik.models import User, Photo
from requests import get
import json
import re

class Command(BaseCommand):
    help = 'Read commons file info'

    def handle(self, *args, **options):
        commons=[
"File:Ajapaik-rephoto-2018-09-20 22-58-01.jpg",
"File:Ajapaik-rephoto-2018-09-19 16-26-56.jpg",
"File:Ajapaik-rephoto-2018-09-19 12-55-44.jpg",
"File:Ajapaik-rephoto-2018-09-18 13-59-54.jpg",
"File:Ajapaik-rephoto-2018-09-18 11-19-52.jpg",
"File:Ajapaik-rephoto-2018-09-18 11-13-59.jpg",
"File:Ajapaik-rephoto-2018-09-18 11-11-28.jpg",
"File:Ajapaik-rephoto-2018-09-16 14-58-09.jpg",
"File:Ajapaik-rephoto-2018-09-16 14-59-41.jpg",
"File:Ajapaik-rephoto-2018-09-16 14-52-47.jpg",
"File:Ajapaik-rephoto-2018-09-16 14-40-29.jpg",
"File:Ajapaik-rephoto-2018-09-14 15-07-39.jpg",
"File:Ajapaik-rephoto-2018-09-16 14-49-11.jpg",
"File:Ajapaik-rephoto-2018-09-14 15-05-44.jpg",
"File:Ajapaik-rephoto-2019-09-11 15-46-19.jpg",
"File:Ajapaik-rephoto-2021-10-29 15-04-08.jpg"]

        # user: 44387121 = Kimmo
        # user: 47476736 = Zache
#        photos = Photo.objects.filter()
        for cfile in commons:
            print("----")
            print(cfile)
            cfile=cfile.replace("File:", "").strip().replace(" ", "_")
            photos = Photo.objects.filter(image__contains=cfile)
            print(photos.count())
            for p in photos:
                print(p.rephoto_of.description)
                print(p.user.get_display_name)
                print("https://ajapaik.ee//photo/" + str(p.id))
