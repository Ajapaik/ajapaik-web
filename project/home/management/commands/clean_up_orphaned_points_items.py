# from django.core.management.base import BaseCommand
# from project.home.models import GeoTag, Points
#
# class Command(BaseCommand):
#     help = "Clean up points items that no longer have a rephoto or geotag"
#     args = "photo_id"
#
#     def handle(self, *args, **options):
#         rephoto_points = Points.objects.filter(action=Points.REPHOTO)
#         for rp in rephoto_points:
#             try:
#                 rephoto = Photo.objects.filter(pk=rp.action_reference).get()