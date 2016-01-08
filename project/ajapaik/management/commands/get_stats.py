# -*- coding: utf-8 -*-
import codecs
import sys
from django.core.management import BaseCommand
from django.db.models import Q
from project.ajapaik.models import Profile, Photo, Points, PhotoComment, PhotoLike, _calc_trustworthiness
from project.ajapaik.settings import ABSOLUTE_PROJECT_ROOT

reload(sys)
sys.setdefaultencoding('utf8')

class Command(BaseCommand):
    help = 'Get some stats for Vahur'

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(Q(score__gt=0) | Q(fb_name__isnull=False) |
                                          Q(google_plus_name__isnull=False) |
                                          Q(user__first_name__isnull=False, user__last_name__isnull=False))\
            .distinct('user_id')
        results = codecs.open(ABSOLUTE_PROJECT_ROOT + '/project/ajapaik/management/commands/results/results.txt', 'w', 'utf-8')
        results.write('id\tname\tfb_name\tfb_email\tgoogle_name\tgoogle_email\tscore\ttrustworthiness\tfirst_geotag\tlatest_geotag\tgeotag_count\tfirst_rephoto\tlatest_rephoto\trephoto_count\tfirst_curation\tlatest_curation\tcuration_count\tfirst_recuration\tlatest_recuration\trecuration_count\tfb_comment_count\tfavorite_count\n')
        for p in profiles:
            first_geotag = p.geotags.order_by('created').first()
            if first_geotag:
                first_geotag = first_geotag.created
            latest_geotag = p.geotags.order_by('-created').first()
            trustworthiness = _calc_trustworthiness(p.user_id)
            if latest_geotag:
                latest_geotag = latest_geotag.created
            geotag_count = p.geotags.count()
            first_rephoto = Photo.objects.filter(rephoto_of__isnull=False, user_id=p.user_id).order_by('created').first()
            if first_rephoto:
                first_rephoto = first_rephoto.created
            latest_rephoto = Photo.objects.filter(rephoto_of__isnull=False, user_id=p.user_id).order_by('-created').first()
            if latest_rephoto:
                latest_rephoto = latest_rephoto.created
            rephoto_count = Photo.objects.filter(rephoto_of__isnull=False, user_id=p.user_id).count()
            first_curation = Points.objects.filter(action=Points.PHOTO_CURATION, user_id=p.user_id).order_by('created').first()
            if first_curation:
                first_curation = first_curation.created
            latest_curation = Points.objects.filter(action=Points.PHOTO_CURATION, user_id=p.user_id).order_by('-created').first()
            if latest_curation:
                latest_curation = latest_curation.created
            curation_count = Points.objects.filter(action=Points.PHOTO_CURATION, user_id=p.user_id).count()
            first_recuration = Points.objects.filter(action=Points.PHOTO_RECURATION, user_id=p.user_id).order_by('created').first()
            if first_recuration:
                first_recuration = first_recuration.created
            latest_recuration = Points.objects.filter(action=Points.PHOTO_RECURATION, user_id=p.user_id).order_by('-created').first()
            if latest_recuration:
                latest_recuration = latest_recuration.created
            recuration_count = Points.objects.filter(action=Points.PHOTO_RECURATION, user_id=p.user_id).count()
            fb_comment_count = PhotoComment.objects.filter(fb_user_id=p.fb_id).count()
            favorite_count = PhotoLike.objects.filter(profile=p).count()
            if not p.fb_name:
                p.fb_name = 'None'
            if not p.google_plus_name:
                p.google_plus_name = 'None'
            if not p.fb_email:
                p.fb_email = 'None'
            if not p.google_plus_email:
                p.google_plus_email = 'None'
            if p.user.get_full_name():
                p.full_name = p.user.get_full_name()
            else:
                p.full_name = 'None'
            results.write('\t'.join([str(p.id), p.full_name, p.fb_email, p.google_plus_name, p.google_plus_email, str(p.score), str(trustworthiness),
                                     str(first_geotag), str(latest_geotag), str(geotag_count), str(first_rephoto),
                                     str(latest_rephoto), str(rephoto_count), str(first_curation), str(latest_curation),
                                     str(curation_count), str(first_recuration), str(latest_recuration),
                                     str(recuration_count), str(fb_comment_count), str(favorite_count), '\n']))
        results.close()