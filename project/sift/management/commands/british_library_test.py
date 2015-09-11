from lxml import etree
import urllib2
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.translation import activate
from project.sift.models import CatAlbum, CatPhoto, Source
from project.sift.settings import ABSOLUTE_PROJECT_ROOT


class Command(BaseCommand):
    help = 'Extract data from XML and download images for BL collection'
    args = 'ap_album_id'

    def handle(self, *args, **options):
        activate('en')
        parser = etree.XMLParser(encoding='utf-8', recover=True)
        tree = etree.parse(ABSOLUTE_PROJECT_ROOT + '/project/sift/management/commands/early-photographically-illustrated-books.xml', parser)
        album = CatAlbum.objects.get(pk=11)
        source = Source.objects.get(pk=59)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36')]
        count = 0
        for item in tree.getroot().iterchildren('item'):
            count += 1
            if count > 144:
                cp = CatPhoto(
                    title=item.find('title').text.strip(),
                    author=item.find('item_creator').text.strip(),
                    source=source,
                    source_url=item.find('url').text.strip(),
                    source_key=item.find('uid').text.strip()
                )
                try:
                    img_response = opener.open(item.find('full_image_url').text)
                    cp.image.save('bl.jpg', ContentFile(img_response.read()))
                    cp.save()
                    album.photos.add(cp)
                except urllib2.HTTPError:
                    print "Not found"
                    print item.find('full_image_url').text
            print count
        album.save()