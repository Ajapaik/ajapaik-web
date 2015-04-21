# coding=utf-8
import urllib2
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from lxml import html
from django.utils import translation
import requests
from project.home.models import Area, Album, Source, Photo, Licence, AlbumPhoto


class Command(BaseCommand):
    help = "Scrape specific URLs from Europeana"

    def handle(self, *args, **options):
        urls = [
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_299600.html?start=13&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_690026.html?start=115&query=where%3Ag%C3%B6teborg&startPage=97&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_300042.html?start=15&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_307247.html?start=16&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_307478.html?start=17&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_319506.html?start=18&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_690014.html?start=23&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_307905.html?start=26&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_309814.html?start=27&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_310029.html?start=28&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_316942.html?start=29&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_318136.html?start=32&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_722928.html?start=39&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_722183.html?start=38&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_326322.html?start=37&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_398207.html?start=60&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_688940.html?start=66&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_690069.html?start=70&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_721782.html?start=71&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/91674/GSM_delobjekt_226922.html?start=86&query=where%3Ag%C3%B6teborg&startPage=1&qf=TYPE%3AIMAGE&qf=YEAR%3A1900&qt=false&rows=96&format=labels"
        ]
        area = Area.objects.filter(name='Göteborg').first()
        if not area:
            new_area = Area(name='Göteborg')
            new_area.save()
            area = new_area
        new_album = Album(name='Göteborg', atype=Album.COLLECTION, is_public=True, profile_id=38)
        new_album.save()
        translation.activate('sv')
        for url in urls:
            result = requests.get(url)
            tree = html.fromstring(result.text)
            image_url = tree.xpath('//td[@property="isShownBy http://www.europeana.eu/schemas/edm/isShownBy"]/text()')[0]
            source_url = tree.xpath('//td[@property="isShownAt http://www.europeana.eu/schemas/edm/isShownAt"]/text()')[0]
            source = Source.objects.get(description='Göteborgs stadsmuseum')
            description = tree.xpath('//span[@property="description http://purl.org/dc/elements/1.1/description"]/text()')[0]
            if not description:
                description = tree.xpath('//span[@property="spatial http://purl.org/dc/terms/spatial"]/text()')[0]
            new_photo = Photo(
                description = description,
                source_key = source_url.split('/')[-1],
                source=source,
                source_url = source_url,
                area=area,
                licence=Licence.objects.get(name="Attribution-ShareAlike 4.0 International"),
            )
            new_photo.save()
            opener = urllib2.build_opener()
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
            img_response = opener.open(image_url)
            new_photo.image.save("europeana.jpg", ContentFile(img_response.read()))
            new_photo.width = new_photo.image.width
            new_photo.height = new_photo.image.height
            AlbumPhoto(album=new_album, photo=new_photo).save()

