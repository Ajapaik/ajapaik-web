import urllib2
import simplejson as json
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import translation
from project.ajapaik.models import Source, Licence, Album, Photo, AlbumPhoto, GeoTag
from project.ajapaik.settings import FLICKR_API_KEY


# This script was made for a single use, review before running
class Command(BaseCommand):
    help = 'Download a set from Flickr'

    @staticmethod
    def _resource_already_exists(key):
        existing = Photo.objects.filter(source_key=key).first()
        if existing:
            return True
        else:
            return False

    def handle(self, *args, **options):
        translation.activate('en')
        set_id = '72157652352869904'
        page = 1
        set_url = 'https://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=' + FLICKR_API_KEY + '&photoset_id=' + set_id + '&extras=license,owner_name,geo,tags&format=json&nojsoncallback=1&page=' + str(page)
        # https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)
        image_url_template = 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg'
        # https://www.flickr.com/photos/{user-id}/{photo-id}
        reference_url_template = 'https://www.flickr.com/photos/%s/%s'
        request = urllib2.Request(set_url)
        response = urllib2.urlopen(request)
        data = response.read()
        data = json.loads(data)
        source = Source.objects.filter(description='Flickr').first()
        if not source:
            source = Source(
                name='Flickr',
                description='Flickr'
            )
            source.save()
        licence = Licence.objects.get(name='Attribution License')
        album = Album.objects.get(pk=1089)
        for photo in data['photoset']['photo']:
            if not self._resource_already_exists(photo['id']):
                new_photo = Photo(
                    source=source,
                    source_url=reference_url_template % (photo['ownername'], photo['id']),
                    source_key=photo['id'],
                    keywords=photo['tags'],
                    licence=licence,
                    description=photo['title'],
                    author='CeriC'
                )
                try:
                    image_url = image_url_template % (photo['farm'], photo['server'], photo['id'], photo['secret'])
                    opener = urllib2.build_opener()
                    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36")]
                    img_response = opener.open(image_url)
                    new_photo.image.save("ceric.jpg", ContentFile(img_response.read()))
                    new_photo.save()
                    if photo['latitude'] and photo['longitude']:
                        source_geotag = GeoTag(
                            lat=photo['latitude'],
                            lon=photo['longitude'],
                            origin=GeoTag.SOURCE,
                            type=GeoTag.SOURCE_GEOTAG,
                            map_type=GeoTag.NO_MAP,
                            photo=new_photo,
                            is_correct=True,
                            trustworthiness=0.2
                        )
                        source_geotag.save()
                        new_photo.latest_geotag = source_geotag.created
                    new_photo.set_calculated_fields()
                    new_photo.save()
                    ap = AlbumPhoto(album=album, photo=new_photo)
                    ap.save()
                    if not album.cover_photo:
                        album.cover_photo = new_photo
                        album.light_save()
                except:
                    print "Problem loading image %s" % photo['id']
                    continue
        album.save()