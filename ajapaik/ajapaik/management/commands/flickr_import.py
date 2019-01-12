import json
from urllib.request import Request, urlopen, build_opener

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import translation
from ajapaik.ajapaik.models import Source, Licence, Album, Photo, Area, AlbumPhoto
from ajapaik.settings import FLICKR_API_KEY


# This script was made for a single use, review before running
class Command(BaseCommand):
    help = 'Will download photos from Flickr'
    args = 'tag page'

    @staticmethod
    def _resource_already_exists(photo_id):
        try:
            Photo.objects.get(source_key=photo_id)
            return True
        except ObjectDoesNotExist:
            return False

    def handle(self, *args, **options):
        translation.activate('en')
        tag = args[0]
        page = args[1]
        search_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=' + FLICKR_API_KEY + '&tags=' + tag + '&is_commons=1&content_type=6&extras=license,original_format&format=json&nojsoncallback=1&page=' + page
        # https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)
        image_url_template = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg'
        # https://www.flickr.com/photos/{user-id}/{photo-id}
        reference_url_template = 'https://www.flickr.com/photos/%s/%s'
        request = Request(search_url)
        response = urlopen(request)
        data = response.read()
        # Testing
        # data = open(ABSOLUTE_PROJECT_ROOT + '/ajapaik/home/management/commands/flickr_import_test.json', 'r').read()
        data = json.loads(data)
        source = Source.objects.get(description='The British Library')
        licence = Licence.objects.get(name='No known copyright restrictions')
        album = Album.objects.get(name='The British Library Metropolitan Improvements')
        area = Area.objects.get(name='London')
        for photo in data['photos']['photo']:
            if photo['license'] == '7' and not self._resource_already_exists(photo['id']):
                new_photo = Photo(
                    source=source,
                    source_url=reference_url_template % (photo['owner'], photo['id']),
                    source_key=photo['id'],
                    date_text='1830',
                    licence=licence,
                    description=photo['title'],
                    area=area,
                    author='Shepherd, Thomas Hosmer'
                )
                try:
                    image_url = image_url_template % (photo['farm'], photo['server'], photo['id'], photo['secret'])
                    opener = build_opener()
                    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                    img_response = opener.open(image_url)
                    new_photo.image.save("tbl.jpg", ContentFile(img_response.read()))
                    new_photo.save()
                    ap = AlbumPhoto(album=album, photo=new_photo)
                    ap.save()
                except:
                    #print "Problem loading image"
                    continue