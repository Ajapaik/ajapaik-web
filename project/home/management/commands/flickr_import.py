import urllib2
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from project.home.models import Source, Licence
from project.settings import ABSOLUTE_PROJECT_ROOT, FLICKR_API_KEY


class Command(BaseCommand):
    help = 'Will download photos from Flickr'
    args = 'tag page'

    def handle(self, *args, **options):
        tag = args[0]
        page = args[1]
        search_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=' + FLICKR_API_KEY + '&tags=' + tag + '&is_commons=1&content_type=6&extras=license,original_format&format=json&nojsoncallback=1&page=' + page
        #https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)
        image_url_template = 'https://farm%s.staticflickr.com/%s/%s_%s_o.%s'
        #request = urllib2.Request(search_url)
        #response = urllib2.urlopen(request)
        #data = response.read()
        data = open(ABSOLUTE_PROJECT_ROOT + '/project/home/management/commands/flickr_import_test.json', 'r').read()
        data = json.loads(data)
        source = Source.objects.get(description='The British Library')
        licence = Licence.objects.get(name='No known copyright restrictions')
        for photo in data['photos']['photo'][0:1]:
            if photo['license'] == '7':
                print photo['title']
                image_url = image_url_template % (photo['farm'], photo['server'], photo['id'], photo['originalsecret'], photo['originalformat'])
                opener = urllib2.build_opener()
                opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                img_response = opener.open(image_url)
                print img_response