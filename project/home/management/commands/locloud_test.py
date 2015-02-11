from lxml import etree

class Command(BaseCommand):
    help = "Will test enriching Locloud XML"
    args = ""

    def handle(self, *args, **options):
        f = open('locloud_test_data.xml', 'r')
        parser = etree.XMLParser()
        data = etree.fromstring(f.read(), parser=parser)
        print data