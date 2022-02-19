import time
from random import randint

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db.models import Sum

from ajapaik.ajapaik.models import Photo, Album, ImageSimilarity


class Command(BaseCommand):
    help = 'Update photo directory from ./media/uploads to ./media/uploads/YYYY/MM'

    def handle(self, *args, **options):

        def get_historical_photo_qs():
            # Populate parent+subalbums list
            sa_ids = [a.id]
            for sa in a.subalbums.filter(atype__in=[Album.CURATED, Album.PERSON]):
                sa_ids.append(sa.id)

            # Get photos
            qs = Photo.objects.filter(rephoto_of__isnull=True).prefetch_related('albumphoto').filter(
                albumphoto__album__in=sa_ids)
            return qs.distinct('id').only('id').order_by()

        # Actual update loop
        albums = Album.objects.exclude(atype__in=[Album.AUTO, Album.FAVORITES])
        for a in albums:
            start_time = time.time()

            historic_photo_qs = get_historical_photo_qs()

            # Flat list of photo_ids for SQL-queries
            historic_photos_list = list(historic_photo_qs.values_list('id', flat=True))

            # Number of historical photos
            a.photo_count_with_subalbums = len(historic_photos_list)

            # Move to next album if there is no photos
            if a.photo_count_with_subalbums == 0:
                continue

            # Number of geotagged photos
            geotagged_photo_qs = historic_photo_qs.filter(lat__isnull=False, lon__isnull=False).order_by()
            a.geotagged_photo_count_with_subalbums = geotagged_photo_qs.count()

            # Get rephoto qs
            rephoto_qs = Photo.objects.filter(rephoto_of__in=historic_photos_list).distinct('id').values(
                'id').order_by()

            # create all_photos_list from historical photos and add rephotos to it to keep backwards
            # compatibility with older stats
            #
            # IMPORTANT: all_photos_list is shallow copy, so it is referencing to same item than historic_photos_list
            # This means that historic_photos_list will include the rephotos too.

            all_photos_list = historic_photos_list

            for p in rephoto_qs:
                all_photos_list.append(p['id'])

            # Finally, calculate rephoto count
            a.rephoto_count_with_subalbums = len(all_photos_list) - a.photo_count_with_subalbums

            # Comment count
            comment_count = Photo.objects.filter(id__in=all_photos_list, comment_count__gt=0).order_by().aggregate(
                Sum('comment_count'))['comment_count__sum']

            a.comments_count_with_subalbums = comment_count or 0

            # Similar photos and confirmed similar photos count
            image_similarity_qs = ImageSimilarity.objects.filter(from_photo__in=all_photos_list).only('pk').distinct(
                'pk').order_by()
            a.similar_photo_count_with_subalbums = image_similarity_qs.count()
            a.confirmed_similar_photo_count_with_subalbums = image_similarity_qs.filter(confirmed=True).count()

            print(str(a) + "(" + str(a.id) + ")\t" + str(a.photo_count_with_subalbums) + "\t" + str(
                time.time() - start_time))

            # Update cover photo and set missing coordinates
            if not a.lat and not a.lon and a.geotagged_photo_count_with_subalbums:
                random_index = randint(0, a.geotagged_photo_count_with_subalbums - 1)
                random_photo_id = geotagged_photo_qs[random_index]
                random_photo = Photo.objects.get(pk=random_photo_id)
                a.lat = random_photo.lat
                a.lon = random_photo.lon
                a.geography = Point(x=float(a.lon), y=float(a.lat), srid=4326)
            else:
                random_index = randint(0, a.photo_count_with_subalbums - 1)
                random_photo = Photo.objects.get(pk=historic_photos_list[random_index])

            a.cover_photo = random_photo
            if random_photo.flip:
                a.cover_photo_flipped = random_photo.flip

            a.light_save()
