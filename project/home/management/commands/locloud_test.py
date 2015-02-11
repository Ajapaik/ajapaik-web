from lxml import etree
from django.core.management.base import BaseCommand
from project.settings import ABSOLUTE_PROJECT_ROOT

class Command(BaseCommand):
    help = "Will test enriching Locloud XML"
    args = ""

    def handle(self, *args, **options):
        f = open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/locloud_test_data.xml', 'r')
        parser = etree.XMLParser()
        data = etree.fromstring(f.read(), parser=parser)
        namespaces = {'edm': 'http://www.europeana.eu/schemas/edm/', 'dc': 'http://purl.org/dc/elements/1.1/'}
        edmProvidedCHO = data.find('edm:ProvidedCHO', namespaces)
        identifier = edmProvidedCHO.find('dc:identifier', namespaces)
        print identifier.text