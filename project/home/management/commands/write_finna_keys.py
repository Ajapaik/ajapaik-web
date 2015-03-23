from lxml import etree
from urllib import urlencode
import urllib2
from urlparse import urlsplit, parse_qs, urlunsplit
from django.core.management.base import BaseCommand
from math import ceil
from project.home.models import CatPhoto


class Command(BaseCommand):
    help = "Finna keys for Signe"
    args = "url"

    @staticmethod
    def _set_query_parameter(url, param_name, param_value):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params[param_name] = [param_value]
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))

    @staticmethod
    def _update_photos_from_xml_response(xml_response):
        for elem in xml_response:
            if elem.tag == "docs":
                photo = CatPhoto.objects.get(source_url=elem.find("record_link").text)
                photo.source_key = elem.find("identifier").text
                photo.save()

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
        self._update_photos_from_xml_response(xml_response)
        if pages_to_get > 1:
            while page < pages_to_get:
                page += 1
                url = self._set_query_parameter(url, 'page', page)
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                data = etree.fromstring(response.read(), parser=parser)
                xml_response = data.find("response")
                self._update_photos_from_xml_response(xml_response)