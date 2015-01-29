from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from project.home.models import GeoTag, Points, Photo

class Command(BaseCommand):
    help = "Clean up points items that no longer have a rephoto or geotag"

    def handle(self, *args, **options):
        rephoto_points = Points.objects.filter(action=Points.REPHOTO)
        for rp in rephoto_points:
            try:
                rephoto = Photo.objects.filter(pk=rp.action_reference).get()
            except ObjectDoesNotExist:
                print "Deleting rephoto points for %i" % rp.action_reference
                rp.delete()
        geotag_points = Points.objects.filter(action=Points.GEOTAG)
        for gp in geotag_points:
            try:
                geotag = GeoTag.objects.filter(pk=gp.action_reference).get()
            except ObjectDoesNotExist:
                print "Deleting geotag points for %i" % gp.id
                gp.delete()