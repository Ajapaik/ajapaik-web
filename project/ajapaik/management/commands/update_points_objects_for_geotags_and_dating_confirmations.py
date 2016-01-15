from django.core.management.base import BaseCommand
from project.ajapaik.models import DatingConfirmation, Points, GeoTag


class Command(BaseCommand):
    help = 'Sets photo field for GeoTag Points, DatingConfirmation Points'

    def handle(self, *args, **options):
        dc_count = DatingConfirmation.objects.count()
        print 'Confirmations in database: %d' % dc_count
        dc_points = Points.objects.filter(action=Points.DATING_CONFIRMATION).prefetch_related('dating_confirmation__confirmation_of__photo')
        print 'Confirmation points in database: %d' % dc_points.count()
        for each in dc_points:
            each.photo_id = each.dating_confirmation.confirmation_of.photo_id
            each.save()
        geotag_count = GeoTag.objects.count()
        print 'Geotags in database: %d' % geotag_count
        geotag_points = Points.objects.filter(action=Points.GEOTAG)
        print 'Geotag points in database: %d' % geotag_points.count()
        i = 0
        while True:
            qs = Points.objects.filter(action=Points.GEOTAG).prefetch_related('geotag__photo')[i * 10000:(i + 1) * 10000]
            for each in qs:
                each.photo = each.geotag.photo
            Points.bulk.bulk_update(qs, update_fields=['photo_id'])
            print "Done"
            i += 1
            if i > 15:
                break
        qs = Points.objects.filter(action=Points.GEOTAG, photo_id__isnull=True).prefetch_related('geotag__photo')
        for each in qs:
            each.photo = each.geotag.photo
        Points.bulk.bulk_update(qs, update_fields=['photo_id'])