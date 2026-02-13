import datetime

from django.core.management import BaseCommand

from ajapaik.ajapaik.models import Profile


class Command(BaseCommand):
    help = 'Find and delete profiles/users that have no data attached (just people who have arrived ' \
           'at the page and never done anything)'


    def handle(self, *args, **options):
        deleted = 0
        print("starting command")
        profiles = Profile.objects.filter(score=0)
        print("we have profiles")
        existing_profile_ids = Profile.objects.exclude(
                photos__isnull=True,
                albums__isnull=True,
                user_last_modified__isnull=True,
                image_similarity_proposer__isnull=True,
                transcriptions__isnull=True,
                transcription_feedback__isnull=True,
                photo_scene_suggestions__isnull=True,
                photo_viewpoint_elevation_suggestions__isnull=True,
                album_photo_links__isnull=True,
                datings__isnull=True,
                dating_confirmations__isnull=True,
                difficulty_feedbacks__isnull=True,
                geotags__isnull=True,
                points__isnull=True,
                skips__isnull=True,
                likes__isnull=True,
                subject_data_proposer__isnull=True,
                face_recognition_rectangle_feedback__isnull=True,
                face_recognition_suggestions__isnull=True,
                face_recognition_rectangles__isnull=True,
                objectdetectionannotation__isnull=True,
                objectdetectionannotationfeedback__isnull=True,
        ).values_list("pk", flat=True)
        print("We have profile ids with relations")
        profile_ids = profiles.filter(
                # Own fields
                first_name__isnull=True,
                last_name__isnull=True,

                fb_name__isnull=True,
                fb_link__isnull=True,
                fb_id__isnull=True,
                fb_token__isnull=True,
                fb_hometown__isnull=True,
                fb_current_location__isnull=True,
                fb_birthday__isnull=True,
                fb_email__isnull=True,
                fb_user_friends__isnull=True,

                google_plus_id__isnull=True,
                google_plus_email__isnull=True,
                google_plus_link__isnull=True,
                google_plus_name__isnull=True,
                google_plus_token__isnull=True,
                google_plus_picture__isnull=True,
                deletion_attempted__isnull=True,
            ).values_list("pk", flat=True)
        print("We have ids")
        print(len(profile_ids))
        print(len(existing_profile_ids))
        to_delete_ids = set(profile_ids).difference(set(existing_profile_ids))
        print(len(to_delete_ids))

        while deleted < 13200000:
            Profile.objects.filter(pk__in=to_delete_ids).delete()
        print("deleted something", deleted)

