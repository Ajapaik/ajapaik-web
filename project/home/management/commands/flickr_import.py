from lxml import etree
from urllib import urlencode
import urllib2
from urlparse import urlsplit, parse_qs, urlunsplit
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from math import ceil
from django.utils import translation
from project.home.models import Source, Photo, Album, AlbumPhoto, Area
from project.settings import ABSOLUTE_PROJECT_ROOT, FLICKR_API_KEY


class Command(BaseCommand):
    help = "Will download photos from Flickr"
    args = "tag"

    def handle(self, *args, **options):
        tag = args[0]
        search_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=' + FLICKR_API_KEY + '&tags=' + tag + '&is_commons=&format=json&nojsoncallback=1'
