from django.contrib.sitemaps import Sitemap
from project.ajapaik.models import Photo
from django.core.urlresolvers import reverse

class PhotoSitemap(Sitemap):
    priority = 0.75

    def items(self):
        return Photo.objects.all()

    def lastmod(self, obj):
        return obj.modified


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['map', 'game', 'leaderboard', 'top50', 'frontpage', 'feed']

    def location(self, item):
        return reverse(item)