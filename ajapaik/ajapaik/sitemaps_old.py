from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from ajapaik.ajapaik.models import Photo


class PhotoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        # Fetch only 'id' and 'modified' fields to optimize the query
        return Photo.objects.only('id', 'modified')

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        # Construct the URL directly using the object's 'id'
        return f"/photo/{obj.id}/"


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['map', 'game', 'leaderboard', 'top50', 'frontpage', 'feed', 'donate']

    def location(self, item):
        return reverse(item)
