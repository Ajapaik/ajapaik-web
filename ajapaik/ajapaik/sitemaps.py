from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from ajapaik.ajapaik.models import Photo


class PhotoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Photo.objects.all()

    def lastmod(self, obj):
        return obj.modified


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['map', 'game', 'leaderboard', 'top50', 'frontpage', 'feed', 'donate']

    def location(self, item):
        return reverse(item)
