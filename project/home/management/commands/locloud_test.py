from lxml import etree
from django.core.management.base import BaseCommand
from project.settings import ABSOLUTE_PROJECT_ROOT
from django.core.exceptions import ObjectDoesNotExist
from project.home.models import Source, Photo

class Command(BaseCommand):
    help = "Will test enriching Locloud XML"
    args = ""

    def handle(self, *args, **options):
        f = open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/locloud_test_data.xml', 'r')
        parser = etree.XMLParser()
        data = etree.fromstring(f.read(), parser=parser)
        namespaces = {
            'edm': 'http://www.europeana.eu/schemas/edm/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'wgs84_pos': 'http://www.w3.org/2003/01/geo/wgs84_pos',
        }
        edmProvidedCHO = data.find('edm:ProvidedCHO', namespaces)
        source = edmProvidedCHO.find('dc:source', namespaces).text
        identifier = edmProvidedCHO.find('dc:identifier', namespaces).text
        existing_source = None
        try:
            existing_source = Source.objects.get(description=source)
        except ObjectDoesNotExist:
            print "No such source"
        existing_resource = None
        if existing_source is not None:
            try:
                existing_resource = Photo.objects.get(source=existing_source, source_key=identifier)
            except ObjectDoesNotExist:
                print "No such resource"
        if existing_resource is not None and existing_resource.lat and existing_resource.lon:
            edmPlace = data.find('edm:Place', namespaces)
            if edmPlace is None:
                data.append(etree.SubElement(data, '{http://www.europeana.eu/schemas/edm/}Place'))
            old_sub_lat = edmPlace.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}lat')
            new_sub_lat = etree.SubElement(edmPlace, '{http://www.w3.org/2003/01/geo/wgs84_pos#}lat')
            new_sub_lat.text = str(existing_resource.lat)
            if old_sub_lat is None:
                edmPlace.append(new_sub_lat)
            else:
                edmPlace.replace(old_sub_lat, new_sub_lat)
            old_sub_lon = edmPlace.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}long')
            new_sub_lon = etree.SubElement(edmPlace, '{http://www.w3.org/2003/01/geo/wgs84_pos#}long')
            new_sub_lon.text = str(existing_resource.lon)
            if old_sub_lon is None:
                edmPlace.append(new_sub_lon)
            else:
                edmPlace.replace(old_sub_lon, new_sub_lon)
        print etree.tostring(data)
        #return etree.tostring(data)