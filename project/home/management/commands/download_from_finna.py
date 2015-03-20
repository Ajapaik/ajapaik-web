from lxml import etree
from urllib import urlencode
import urllib2
from urlparse import urlsplit, parse_qs, urlunsplit
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from math import ceil
from project.home.models import CatPhoto, Source, CatAlbum


class Command(BaseCommand):
    help = "Create categorizer test data from Finna"
    args = "url"

    @staticmethod
    def _set_query_parameter(url, param_name, param_value):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params[param_name] = [param_value]
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))

    @staticmethod
    def _create_photos_from_xml_response(xml_response):
        for elem in xml_response:
            if elem.tag == "docs":
                new_photo = CatPhoto(
                    title=elem.find("title").text,
                    description=elem.find("title_sort").text,
                    source=Source.objects.get(description=elem.find('institution').text),
                    source_url=elem.find("record_link").text,
                    date_text=elem.find("main_date_str").text,
                    album=CatAlbum.objects.get(pk=3),
                    author=elem.find("author").text,
                )
                opener = urllib2.build_opener()
                opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                img_response = opener.open(elem.find("image_links").text)
                new_photo.image.save("finna.jpg", ContentFile(img_response.read()))
                new_photo.save()

    def handle(self, *args, **options):
        self.count = 1
        url = args[0]
        items_per_page = 20
        page = 1
        parser = etree.XMLParser()
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        data = etree.fromstring(response.read(), parser=parser)
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