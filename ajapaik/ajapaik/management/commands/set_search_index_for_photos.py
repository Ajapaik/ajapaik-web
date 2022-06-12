from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.conf import settings
from ajapaik.ajapaik.models import Photo, PhotoSearchIndex


class Command(BaseCommand):
    help = "Set geography field for photos"

    def handle(self, *args, **options):
        photos = Photo.objects.filter(rephoto_of__isnull=True)
        for p in photos:
            print(p.title)
            print(p.description)
            search_index=PhotoSearchIndex.objects.filter(photo=p.id).first()

            if not search_index:
                search_index= PhotoSearchIndex()
                search_index.photo=p
            else:
                 search_index.update_vectors()
                 continue

            for lang in settings.MODELTRANSLATION_LANGUAGES:
                print(lang)
                title =  getattr(p,'title_' + str(lang)) or ""
                if not title:
                    title =  getattr(p,'title', "") or ""

                description = getattr(p, 'description_' +str(lang),"")
                if not description:
                    description = getattr(p, 'description', "") or ""

                date_text = getattr(p, 'date_text' + str(lang),"") or ""
                address = getattr(p, 'address' + str(lang),"") or ""
                author = getattr(p, 'author' + str(lang),"") or ""

                index_text = title + "\t" + description + "\t" + date_text + "\t" + address + "\t" + author
                index_key = 'text_' + str(lang)
                setattr(search_index, index_key, index_text)

            search_index.update_vectors()
#            search_index.save()
