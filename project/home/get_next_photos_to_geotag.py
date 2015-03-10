from project.home.models import *
from django.db.models import *
from django.utils.translation import ugettext as _

def calc_trustworthiness(user_id):
    total_tries = 0
    correct_tries = 0
    for row in GeoTag.objects.filter(user=user_id, is_correct__isnull=False, origin=GeoTag.GAME).values('is_correct').annotate(count=Count('pk')):
        total_tries += row['count']
        if row['is_correct']:
            correct_tries += row['count']

    if not correct_tries:
        return 0

    return (1 - 0.9 ** correct_tries) * correct_tries / float(total_tries)

def submit_guess(user, photo_id, lon=None, lat=None, geotag_type=GeoTag.MAP, hint_used=False, azimuth=None, zoom_level=None, azimuth_line_end_point=None, origin=GeoTag.GAME):
    p = Photo.objects.get(pk=photo_id)

    location_correct = False
    location_uncertain = False
    this_guess_score = 0
    azimuth_uncertain = False
    azimuth_correct = False
    feedback_message = ""

    if hint_used == "true":
        hint_used = True
    elif hint_used == "false":
        hint_used = False

    if lon is not None and lat is not None:
        trustworthiness = calc_trustworthiness(user.pk)

        if origin == GeoTag.GAME:
            if p.confidence >= 0.3:
                error_in_meters = distance_in_meters(p.lon, p.lat, float(lon), float(lat))
                this_guess_score = int(130 * max(0, min(1, (1 - (error_in_meters - 15) / float(94 - 15)))))
                location_correct = (this_guess_score > 0)
            else:
                this_guess_score = max(20, int(300 * trustworthiness))
                #if not p.lat and not p.lon:
                if p.user == user:
                    location_correct = True
                location_uncertain = True
            if hint_used:
                this_guess_score *= 0.75
        else:
            this_guess_score = int(trustworthiness * 100)

        all_photo_geotags = p.geotags.all()
        if len(all_photo_geotags) == 1:
            # This is the second geotag coming in, if it's near the first one, mark the first one correct
            if distance_in_meters(all_photo_geotags[0].lat, all_photo_geotags[0].lon, float(lat), float(lon)) < 100:
                all_photo_geotags[0].is_correct = True,
                all_photo_geotags[0].save()

        new_geotag = GeoTag(user=user, photo_id=p.id, type=geotag_type,
                            lat=float(lat), lon=float(lon),
                            is_correct=location_correct,
                            trustworthiness=trustworthiness,
                            zoom_level=zoom_level, origin=origin, hint_used=hint_used)

        if azimuth_line_end_point:
            new_geotag.azimuth_line_end_lat = azimuth_line_end_point[0]
            new_geotag.azimuth_line_end_lon = azimuth_line_end_point[1]

        azimuth_score = 0
        if azimuth:
            new_geotag.azimuth = azimuth
            if not p.azimuth:
                if location_correct and origin == GeoTag.GAME:
                    azimuth_score = max(20, int(300 * trustworthiness))
                azimuth_uncertain = True

        if azimuth and p.azimuth:
            degree_error_point_array = [100, 99, 97, 93, 87, 83, 79, 73, 67, 61, 55, 46, 37, 28, 19, 10]
            azimuth = float(azimuth)
            difference = max(p.azimuth, azimuth) - min(p.azimuth, azimuth)
            if difference > 180:
                difference = 360 - difference
            if int(difference) <= 15:
                azimuth_score = degree_error_point_array[int(difference)]
                azimuth_correct = True
            if azimuth_correct and (location_correct or location_uncertain) and origin == GeoTag.GAME:
                new_geotag.azimuth_score = azimuth_score

        this_guess_score += azimuth_score
        new_geotag.azimuth_score = azimuth_score
        new_geotag.score = this_guess_score
        new_geotag.save()
        new_action = Points(user=user, action=Points.GEOTAG, geotag=new_geotag, points=new_geotag.score, created=datetime.datetime.now())
        new_action.save()
    else:
        Skip(user=user, photo_id=p.id).save()

    p.set_calculated_fields()
    p.save()

    user.set_calculated_fields()
    user.save()

    all_geotags_latlng_for_this_photo = GeoTag.objects.filter(photo_id=photo_id)
    all_geotags_with_azimuth_for_this_photo = all_geotags_latlng_for_this_photo.filter(azimuth__isnull=False)
    all_geotags_latlng_for_this_photo = [[g[0], g[1]] for g in all_geotags_latlng_for_this_photo.values_list("lat", "lon")]
    all_geotag_ids_with_azimuth_for_this_photo = all_geotags_with_azimuth_for_this_photo.values_list("id", flat=True)
    azimuth_tags_count = len(all_geotag_ids_with_azimuth_for_this_photo)
    new_estimated_location = [p.lat, p.lon]

    if origin == GeoTag.GAME:
        if location_correct:
            feedback_message = _("Looks right!")
            if not azimuth:
                feedback_message = _("The location seems right. Try submitting an azimuth to earn even more points!")
            elif azimuth_uncertain:
                feedback_message = _("The location seems right, but the azimuth is yet uncertain.")
                if azimuth_tags_count == 1:
                    feedback_message = _("The location seems right, your azimuth was first.")
            elif not azimuth_correct:
                feedback_message = _("The location seems right, but not the azimuth.")
        elif len(all_geotags_latlng_for_this_photo) == 1:
            feedback_message = _("Your guess was first.")
        elif location_uncertain:
            feedback_message = _("Correct location is not certain yet.")
        elif not location_correct:
            feedback_message = _("Other users have different opinion.")


    return location_correct, location_uncertain, this_guess_score, feedback_message, all_geotags_latlng_for_this_photo, azimuth_tags_count, new_estimated_location, p.confidence


def get_leaderboard(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_recent_activity__gt=0) |
        Q(google_plus_name__isnull=False, score_recent_activity__gt=0) |
        Q(pk=user_id)).values_list('pk', 'score_recent_activity', 'fb_id', 'fb_name', 'google_plus_name', 'google_plus_picture').order_by('-score_recent_activity')))
    leaderboard = [scores_list[0]]
    self_user_idx = filter(lambda (idx, data): data[0] == user_id, scores_list)[0][0]
    if self_user_idx - 1 > 0:
        leaderboard.append(scores_list[self_user_idx - 1])
    if self_user_idx > 0:
        leaderboard.append(scores_list[self_user_idx])
    if self_user_idx + 1 < len(scores_list):
        leaderboard.append(scores_list[self_user_idx + 1])
    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3], data[4], data[5]) for idx, data in leaderboard]
    return leaderboard


def get_leaderboard50(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_recent_activity__gt=0) |
        Q(google_plus_name__isnull=False, score_recent_activity__gt=0) |
        Q(pk=user_id)).values_list('pk', 'score_recent_activity', 'fb_id', 'fb_name', 'google_plus_name', 'google_plus_picture').order_by('-score_recent_activity')))
    leaderboard = scores_list[:50]
    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3]) for idx, data in leaderboard]
    return leaderboard


def get_all_time_leaderboard50(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score__gt=0) |
        Q(google_plus_name__isnull=False, score__gt=0) |
        Q(pk=user_id)).values_list('pk', 'score', 'fb_id', 'fb_name', 'google_plus_name', 'google_plus_picture').order_by('-score')))
    leaderboard = scores_list[:50]
    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3]) for idx, data in leaderboard]
    return leaderboard