from django.core.management import BaseCommand

from project.ajapaik.models import Profile


class Command(BaseCommand):
    help = 'Find and delete profiles/users that have no data attached (just people who have arrived at the page and never done anything)'

    def handle(self, *args, **options):
        offset = 0
        pagesize = 1000
        count = Profile.objects.filter(photos__isnull=True, albums__isnull=True,
                                          album_photo_links__isnull=True, datings__isnull=True,
                                          dating_confirmations__isnull=True, difficulty_feedbacks__isnull=True,
                                          geotags__isnull=True, points__isnull=True, skips__isnull=True,
                                          fb_name__isnull=True, fb_link__isnull=True, fb_id__isnull=True,
                                          fb_token__isnull=True, fb_hometown__isnull=True, fb_birthday__isnull=True,
                                          fb_current_location__isnull=True, fb_email__isnull=True,
                                          fb_user_friends__isnull=True, google_plus_id__isnull=True,
                                          google_plus_email__isnull=True, google_plus_link__isnull=True,
                                          google_plus_name__isnull=True, google_plus_token__isnull=True,
                                          google_plus_picture__isnull=True, first_name__isnull=True,
                                          last_name__isnull=True, likes__isnull=True, tour_groups__isnull=True,
                                          owned_tours__isnull=True, tour_rephotos__isnull=True, tour_views__isnull=True).count()
        print count
        while offset < count:
            for m in Profile.objects.filter(photos__isnull=True, albums__isnull=True,
                                          album_photo_links__isnull=True, datings__isnull=True,
                                          dating_confirmations__isnull=True, difficulty_feedbacks__isnull=True,
                                          geotags__isnull=True, points__isnull=True, skips__isnull=True,
                                          fb_name__isnull=True, fb_link__isnull=True, fb_id__isnull=True,
                                          fb_token__isnull=True, fb_hometown__isnull=True, fb_birthday__isnull=True,
                                          fb_current_location__isnull=True, fb_email__isnull=True,
                                          fb_user_friends__isnull=True, google_plus_id__isnull=True,
                                          google_plus_email__isnull=True, google_plus_link__isnull=True,
                                          google_plus_name__isnull=True, google_plus_token__isnull=True,
                                          google_plus_picture__isnull=True, first_name__isnull=True,
                                          last_name__isnull=True, likes__isnull=True, tour_groups__isnull=True,
                                          owned_tours__isnull=True, tour_rephotos__isnull=True, tour_views__isnull=True)[offset: offset + pagesize].iterator:
                try:
                    m.user.delete()
                    print 'deleted %s' % m.user.id
                except:
                    print 'failed to delete %s' % m.user.id
            offset += pagesize