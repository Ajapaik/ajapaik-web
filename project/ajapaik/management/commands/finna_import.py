from lxml import etree
from urllib import urlencode
import urllib2
from urlparse import urlsplit, parse_qs, urlunsplit
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from math import ceil
from django.utils import translation
from project.ajapaik.models import Source, Photo, Album, AlbumPhoto, Licence
from project.ajapaik.settings import ABSOLUTE_PROJECT_ROOT


# This script was made for a single use, review before running
class Command(BaseCommand):
    help = "Will download data from Finna"
    args = "url target_album"

    @staticmethod
    def _set_query_parameter(url, param_name, param_value):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params[param_name] = [param_value]
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))

    @staticmethod
    def _resource_already_exists(xml_element):
        if xml_element.find('institution') is not None:
            try:
                source = Source.objects.get(description=xml_element.find('institution').text)
            except ObjectDoesNotExist:
                source = Source(name=xml_element.find('institution').text, description=xml_element.find('institution').text)
                source.save()
                return False
        else:
            source = Source.objects.get(name='AJP')
        if xml_element.find('identifier') is not None:
            try:
                existing_resource = Photo.objects.get(source=source, source_key=xml_element.find('identifier').text)
                return True
            except ObjectDoesNotExist:
                return False
        return False

    def _create_photos_from_xml_response(self, xml_response):
        for elem in xml_response:
            if elem.tag == "docs":
                if  not self._resource_already_exists(elem):
                    new_photo = Photo(
                        title=elem.find("title").text,
                        description=elem.find("title_sort").text,
                        source=Source.objects.get(description=elem.find('institution').text),
                        source_key=elem.find("identifier").text,
                        external_id=elem.find("identifier").text,
                        date_text=getattr(elem.find("main_date_str"), 'text', None),
                        author=elem.find("author").text,
                        source_url=elem.find("record_link").text,
                        licence=Licence.objects.filter(url='https://creativecommons.org/about/pdm').first()
                    )
                    opener = urllib2.build_opener()
                    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                    img_response = opener.open(elem.find("image_links").text)
                    new_photo.image.save("finna.jpg", ContentFile(img_response.read()))
                    new_photo.save()
                    ap = AlbumPhoto(album=self.album, photo=new_photo)
                    ap.save()

    def handle(self, *args, **options):
        translation.activate('fi')
        url = args[0]
        target_album = args[1]
        try:
            self.album = Album.objects.get(name=target_album)
        except ObjectDoesNotExist:
            new_album = Album(name=target_album, atype=Album.CURATED, is_public=True)
            new_album.save()
            self.album = new_album
        items_per_page = 20
        page = 1
        parser = etree.XMLParser()
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        data = etree.fromstring(response.read(), parser=parser)
        # For testing
        #f = open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/finna_import_test_xml.xml', 'r')
        #data = etree.fromstring(f.read(), parser=parser)
        xml_response = data.find("response")
        number_of_items = int(xml_response.find("numFound").text)
        pages_to_get = int(ceil(number_of_items / items_per_page))
        self._create_photos_from_xml_response(xml_response)
        if pages_to_get > 1:
            while page < pages_to_get:
                page += 1
                url = self._set_query_parameter(url, 'page', page)
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                data = etree.fromstring(response.read(), parser=parser)
                xml_response = data.find("response")
                self._create_photos_from_xml_response(xml_response)