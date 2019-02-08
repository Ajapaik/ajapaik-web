# coding=utf-8
from urllib.request import build_opener

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from lxml import html
from django.utils import translation
import requests
from ajapaik.ajapaik.models import Area, Album, Source, Photo, Licence, AlbumPhoto


# This script was made for a single use, review before running
class Command(BaseCommand):
    help = "Scrape specific URLs from Europeana"

    def handle(self, *args, **options):
        urls = [
            "http://www.europeana.eu/portal/record/08535/local__default__F_7595.html?start=12&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_7598.html?start=13&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_7599.html?start=14&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_7600.html?start=15&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_3450.html?start=17&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_3451.html?start=18&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_3453.html?start=19&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_3449.html?start=20&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
            "http://www.europeana.eu/portal/record/08535/local__default__F_3452.html?start=21&query=*%3A*&startPage=1&qf=ansicht&qf=where%3Avienna&qf=REUSABILITY%3Arestricted&qf=photograph&qt=false&rows=96&format=labels",
        ]
        area = Area.objects.filter(name='Vienna').first()
        if not area:
            new_area = Area(name='Vienna')
            new_area.lat = '48.2000'
            new_area.lon = '16.3667'
            new_area.save()
            area = new_area
        new_album = Album.objects.filter(name='Vienna, Austria').first()
        if not new_album:
            new_album = Album(
                name='Vienna, Austria',
                atype=Album.CURATED
            )
            new_album.save()
        new_album.save()
        translation.activate('de')
        for url in urls:
            result = requests.get(url)
            tree = html.fromstring(result.text)
            image_url = tree.xpath('//td[@property="isShownBy http://www.europeana.eu/schemas/edm/isShownBy"]/text()')[0]
            source_url = tree.xpath('//td[@property="isShownAt http://www.europeana.eu/schemas/edm/isShownAt"]/text()')[0]
            author = tree.xpath('//span[@property="creator http://purl.org/dc/elements/1.1/creator"]/text()')[0]
            source = Source.objects.filter(name="Architekturmuseum der Technischen Universität Berlin in der Universitätsbibliothek").first()
            if not source:
                source = Source(
                    name="Architekturmuseum der Technischen Universität Berlin in der Universitätsbibliothek",
                    description="Architekturmuseum der Technischen Universität Berlin in der Universitätsbibliothek"
                )
                source.save()
            description = tree.xpath('//span[@property="subject http://purl.org/dc/elements/1.1/subject"]/text()')[0]
            source_key = tree.xpath('//span[@property="identifier http://purl.org/dc/elements/1.1/identifier"]/text()')[0]
            if not description:
                description = tree.xpath('//span[@property="title http://purl.org/dc/terms/title"]/text()')[0]
            new_photo = Photo(
                description = description,
                source_key = source_key,
                source=source,
                source_url = source_url,
                area=area,
                author=author,
                licence=Licence.objects.get(url="http://creativecommons.org/licenses/by-nc-sa/4.0/"),
            )
            new_photo.save()
            opener = build_opener()
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
            img_response = opener.open(image_url)
            new_photo.image.save("europeana.jpg", ContentFile(img_response.read()))
            new_photo.width = new_photo.image.width
            new_photo.height = new_photo.image.height
            AlbumPhoto(album=new_album, photo=new_photo).save()