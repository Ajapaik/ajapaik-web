from django.contrib.sitemaps import Sitemap
from project.sift.models import CatAlbum, CatPhoto
from django.core.urlresolvers import reverse


class AlbumTagSitemap(Sitemap):
    priority = 0.8

    def items(self):
        return CatAlbum.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return reverse('cat_tagger') + '?album=' + str(obj.pk)


class AlbumResultSitemap(Sitemap):
    priority = 0.8

    def items(self):
        return CatAlbum.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return reverse('cat_results') + '?album=' + str(obj.pk)


class StaticViewSitemap(Sitemap):
    priority = 1

    def items(self):
        return ['cat_about', 'cat_results', 'cat_tagger']

    def location(self, item):
        return reverse(item)


class PhotoSitemap(Sitemap):
    priority = 1

    def items(self):
        return CatPhoto.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return reverse('project.sift.views.photo_permalink', args=(obj.pk, obj.slug))