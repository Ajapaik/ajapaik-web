import flickrapi

from project.ajapaik.settings import FLICKR_API_KEY, FLICKR_API_SECRET


class FlickrCommonsDriver(object):
    def __init__(self):
        self.flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET, format='parsed-json')

    def search(self, form):
        return self.flickr.photos.search(text=form.cleaned_data['full_text'], media='photos', is_commons=True,
                                         per_page=200, extras='tags')