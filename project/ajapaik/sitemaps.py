from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from project.ajapaik.models import Photo


class PhotoSitemap(Sitemap):
    priority = 1

    def items(self):
        return Photo.objects.all()

    def lastmod(self, obj):
        return obj.modified


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['map', 'game', 'leaderboard', 'top50', 'frontpage']

    def location(self, item):
        return reverse(item)
