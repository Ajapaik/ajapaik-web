from json import dumps

import flickrapi

from project.ajapaik.models import Photo, AlbumPhoto, Album
from project.ajapaik.settings import FLICKR_API_KEY, FLICKR_API_SECRET


class FlickrCommonsDriver(object):
    def __init__(self):
        self.flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET, format='parsed-json', store_token=False)

    def search(self, cleaned_data):
        return self.flickr.photos.search(text=cleaned_data['fullSearch'], media='photos', is_commons=True, per_page=200,
                                         extras='tags,geo', page=cleaned_data['flickrPage'])

    @staticmethod
    def transform_response(response, remove_existing=False):
        ids = [p['id'] for p in response['photos']['photo']]
        transformed = {
            'result': {
                'firstRecordViews': [],
                'page': response['photos']['page'],
                'pages': response['photos']['pages']
            }
        }
        existing_photos = Photo.objects.filter(source__description='Flickr Commons', external_id__in=ids).all()
        for p in response['photos']['photo']:
            existing_photo = existing_photos.filter(external_id=p['id']).first()
            if remove_existing and existing_photo:
                continue
            else:
                transformed_item = {
                    'isFlickrResult': True,
                    'cachedThumbnailUrl': 'https://farm%s.staticflickr.com/%s/%s_%s_t.jpg' % (
                    p['farm'], p['server'], p['id'], p['secret']),
                    'title': p['title'],
                    'institution': 'Flickr Commons',
                    'imageUrl': 'https://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (
                    p['farm'], p['server'], p['id'], p['secret']),
                    'id': p['id'],
                    'mediaId': p['id'],
                    'identifyingNumber': p['id'],
                    'urlToRecord': 'https://www.flickr.com/photos/%s/%s' % (p['owner'], p['id']),
                    'latitude': p['latitude'],
                    'longitude': p['longitude']
                }
                if existing_photo:
                    transformed_item['ajapaikId'] = existing_photo.id
                    album_ids = AlbumPhoto.objects.filter(photo=existing_photo).values_list('album_id', flat=True)
                    transformed_item['albums'] = Album.objects.filter(pk__in=album_ids, atype=Album.CURATED) \
                        .values_list('id', 'name')
                transformed['result']['firstRecordViews'].append(transformed_item)

        transformed = dumps(transformed)

        return transformed
