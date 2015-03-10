from django.core.management.base import BaseCommand
from project.home.models import Photo, Points, GeoTag

class Command(BaseCommand):
    help = "Will populate the points table from old geotag and rephoto data"

    def handle(self, *args, **options):
        for original in Photo.objects.filter(rephoto_of__isnull=True):
            oldest_rephoto = None
            rephoto_to_user_id_map = {}
            for rephoto in original.rephotos.order_by("created"):
                if not oldest_rephoto:
                    oldest_rephoto = rephoto
                if rephoto.user and rephoto.user.id:
                    try:
                        rephoto_to_user_id_map[rephoto.user.id].append(rephoto)
                    except KeyError:
                        rephoto_to_user_id_map[rephoto.user.id] = [rephoto]
            for k, list in rephoto_to_user_id_map.iteritems():
                first = True
                user_made_oldest = False
                for v in list:
                    if v == oldest_rephoto:
                        oldest_rephoto_points = Points(
                            user=oldest_rephoto.user,
                            action=Points.REPHOTO,
                            photo=oldest_rephoto,
                            points=1250,
                            created=oldest_rephoto.created
                        )
                        user_made_oldest = True
                        oldest_rephoto_points.save()
                    else:
                        if first and not user_made_oldest:
                            oldest_rephoto_by_user_points = Points(
                                user=v.user,
                                action=Points.REPHOTO,
                                photo=v,
                                points=1000,
                                created=v.created
                            )
                            oldest_rephoto_by_user_points.save()
                            first = False
                        else:
                            rephoto_by_same_user_points = Points(
                                user=v.user,
                                action=Points.REPHOTO,
                                photo=v,
                                points=250,
                                created=v.created
                            )
                            rephoto_by_same_user_points.save()
        for geotag in GeoTag.objects.all():
            geotag_points_item = Points(
                user=geotag.user,
                action=Points.GEOTAG,
                geotag=geotag,
                points=geotag.score,
                created=geotag.created
            )
            geotag_points_item.save()
            print geotag_points_item.id