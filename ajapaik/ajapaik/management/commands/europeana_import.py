from urllib.request import build_opener

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.management import BaseCommand
from django.utils import translation

from ajapaik.ajapaik.models import Area, Album, Source, Photo, AlbumPhoto


# TODO: Old API, remake?
class Command(BaseCommand):
    help = "Will download data from Europeana"
    args = "query geoname target_album text_language"

    @staticmethod
    def _resource_already_exists(provider=None, identifier=None):
        if provider is not None:
            try:
                source = Source.objects.get(description=provider)
            except ObjectDoesNotExist:
                source = Source(name=provider, description=provider)
                source.save()
                return False
        else:
            source = Source.objects.get(name='AJP')
        if identifier is not None:
            try:
                existing_resource = Photo.objects.get(source=source, source_key=identifier)
                return True
            except ObjectDoesNotExist:
                return False
        return False

    def query_europeana(self, query_term, start=1, size=96):
        qf_buf = []
        qf_buf.append("TYPE:IMAGE")
        arguments = {
            'wskey': settings.EUROPEANA_API_KEY,
            'query': query_term,
            'qf': qf_buf,
            'start': str(start),
            'rows': str(size),
            'profile': 'rich'
        }
        results = requests.get(self.query_url, params=arguments).json()
        return results

    def handle(self, *args, **options):
        self.query_url = "http://europeana.eu/api/v2/search.json"
        self.resource_url = "http://europeana.eu/api/v2/record"
        query = args[0]
        geoname = args[1]
        album_name = args[2]
        text_language = args[3]
        translation.activate('en')
        try:
            area = Area.objects.get(name=geoname)
        except ObjectDoesNotExist:
            new_area = Area(name=geoname)
            new_area.save()
            area = new_area
        try:
            album = Album.objects.get(name=album_name)
        except ObjectDoesNotExist:
            new_album = Album(name=album_name, atype=Album.COLLECTION, is_public=True)
            new_album.save()
            album = new_album
        translation.activate(text_language)
        query_result = self.query_europeana(query)
        item_count = int(query_result["itemsCount"])
        ret = []
        for i in xrange(0, item_count):
            if "dataProvider" in query_result["items"][i] and "id" in query_result["items"][i]:
                if not self._resource_already_exists(query_result["items"][i]["dataProvider"][0],
                                                     query_result["items"][i]["id"]):
                    new_photo = Photo(
                        area=area,
                        source=Source.objects.get(description=query_result["items"][i]["dataProvider"][0]),
                        source_key=query_result["items"][i]["id"],
                        licence="Public domain"
                    )
                    if "edmIsShownAt" in query_result["items"][i]:
                        new_photo.source_url = query_result["items"][i]["edmIsShownAt"][0]
                    if "edmAgentLabel" in query_result["items"][i]:
                        new_photo.author = query_result["items"][i]["edmAgentLabel"][0]["def"]
                    if "title" in query_result["items"][i]:
                        new_photo.description = query_result["items"][i]["title"][0]
                    opener = build_opener()
                    opener.addheaders = [("User-Agent",
                                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                    try:
                        img_response = opener.open(query_result["items"][i]["edmIsShownBy"][0])
                        new_photo.image.save("europeana.jpg", ContentFile(img_response.read()))
                        new_photo.save()
                        ap = AlbumPhoto(album=album, photo=new_photo)
                        ap.save()
                    except:
                        pass
