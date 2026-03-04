from random import randint

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.timezone import now

from ajapaik.ajapaik.models import Photo, Album, ImageSimilarity


class Command(BaseCommand):
    help = 'Update albums'

    def handle(self, *args, **options):

        # Actual update loop
        albums = Album.objects.exclude(atype__in=[Album.AUTO, Album.FAVORITES])
        print(f"Updating {albums.count()} albums, start time: {now()}")

        for a in albums:
            modified_fields = [
                'photo_count_with_subalbums',
                'geotagged_photo_count_with_subalbums',
                'rephoto_count_with_subalbums',
                'comments_count_with_subalbums',
                'similar_photo_count_with_subalbums',
                'confirmed_similar_photo_count_with_subalbums',
                'cover_photo',
            ]
            historic_photo_qs = a.get_historic_photos_queryset_with_subalbums()

            # Flat list of photo_ids for SQL-queries
            historic_photo_ids = list(historic_photo_qs.values_list('id', flat=True))

            # Number of historical photos
            a.photo_count_with_subalbums = len(historic_photo_ids)

            # Move to next album if there are no photos
            if a.photo_count_with_subalbums == 0:
                continue

            # Number of geotagged photos
            geotagged_photo_qs = historic_photo_qs.filter(lat__isnull=False, lon__isnull=False).order_by()
            a.geotagged_photo_count_with_subalbums = geotagged_photo_qs.count()

            # Get rephoto qs
            rephoto_ids = list(
                Photo.objects.filter(rephoto_of_id__in=historic_photo_ids).distinct('id').values_list(
                    'id', flat=True
                ).order_by())

            # create all_photos_list from historical photos and add rephotos to it to keep backwards compatible
            # with older stats
            #
            # IMPORTANT: all_photos_list is shallow copy so it is referencing to same item than historic_photo_ids_list
            # This means that historic_photo_ids_list will include the rephotos too.
            all_photo_ids = historic_photo_ids
            all_photo_ids.extend(rephoto_ids)

            ### Finally calculate rephoto count
            a.rephoto_count_with_subalbums = len(rephoto_ids)

            # Comment count
            comment_count = Photo.objects.filter(id__in=all_photo_ids, comment_count__gt=0).order_by().aggregate(
                Sum('comment_count'))['comment_count__sum']
            a.comments_count_with_subalbums = comment_count or 0

            # Similar photos and confirmed similar photos count
            image_similarity_qs = ImageSimilarity.objects.filter(from_photo_id__in=all_photo_ids).only(
                'pk', 'confirmed').distinct('pk').order_by()
            a.similar_photo_count_with_subalbums = image_similarity_qs.count()
            a.confirmed_similar_photo_count_with_subalbums = image_similarity_qs.filter(confirmed=True).count()

            # Update cover photo and set missing coordinates
            if not a.lat and not a.lon and a.geotagged_photo_count_with_subalbums:
                random_index = randint(0, a.geotagged_photo_count_with_subalbums - 1)
                random_photo = geotagged_photo_qs[random_index]
                a.lat = random_photo.lat
                a.lon = random_photo.lon
                a.geography = Point(x=float(a.lon), y=float(a.lat), srid=4326)
                modified_fields.extend(['lat', 'lon', 'geography'])
            else:
                random_index = randint(0, a.photo_count_with_subalbums - 1)
                random_photo = Photo.objects.get(pk=historic_photo_ids[random_index])

            a.cover_photo = random_photo
            if random_photo.flip:
                a.cover_photo_flipped = random_photo.flip
                modified_fields.append('cover_photo_flipped')

            a.light_save(update_fields=modified_fields)

        print(f"Finished updating albums, end time: {now()}")
