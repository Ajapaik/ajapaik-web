from django.contrib.sitemaps import Sitemap
from ajapaik.ajapaik.models import Photo, Video
from django.core.urlresolvers import reverse


class PhotoSitemap(Sitemap):
    priority = 1

    def items(self):
        return Photo.objects.all()

    def lastmod(self, obj):
        return obj.modified


class VideoSitemap(Sitemap):
    priority = 1

    def items(self):
        return Video.objects.all()

    def lastmod(self, obj):
        return obj.modified


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['map', 'game', 'leaderboard', 'top50', 'frontpage', 'feed', 'uudiskiri', 'donate']

    def location(self, item):
        return reverse(item)
