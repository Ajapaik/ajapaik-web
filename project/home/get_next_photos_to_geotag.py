from project.home.models import *
from django.db.models import *
from sorl.thumbnail import get_thumbnail
from django.utils.translation import ugettext as _
import random


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


def calculate_recent_activity_scores():
    recent_actions = Points.objects.order_by('-created')[:10]
    for action in recent_actions:
        print action.created


#
# DEPRICATED see models.Photo
#
def get_next_photos_to_geotag(user_id, nr_of_photos=5, city_id=None):
    #!!! use trustworthiness to select desired level

    trustworthiness = calc_trustworthiness(user_id)

    photos_set = Photo.objects.all()
    if city_id is not None:
        photos_set = photos_set.filter(city__pk=city_id)

    extra_args = {'select': {'final_level':
                                 "(case when level > 0 then level else " + \
                                 "coalesce(guess_level,4) end)"},
                  'where': ['rephoto_of_id IS NULL']}

    forbidden_photo_ids = frozenset([g.photo_id \
                                     for g in Skip.objects.filter(user=user_id,
                                                                  created__gte= \
                                                                      datetime.datetime.now() - datetime.timedelta(
                                                                          1))] + \
                                    list(GeoTag.objects.filter(user=user_id). \
                                             values_list('photo_id', flat=True)))
    known_photos = list(photos_set.exclude(
        pk__in=forbidden_photo_ids). \
                            filter(confidence__gte=0.3). \
                            extra(**extra_args). \
                            order_by('final_level')[:nr_of_photos])

    unknown_photos_to_get = 0
    if trustworthiness > 0.2:
        unknown_photos_to_get = \
            int(nr_of_photos * (0.3 + 1.5 * trustworthiness))
    unknown_photos_to_get = max(unknown_photos_to_get,
                                nr_of_photos - len(known_photos))

    unknown_photos = set()

    if unknown_photos_to_get:
        photo_ids_with_few_guesses = frozenset(
            GeoTag.objects.values('photo_id'). \
                annotate(nr_of_geotags=Count('id')). \
                filter(nr_of_geotags__lte=10). \
                values_list('photo_id', flat=True)) - forbidden_photo_ids
        if photo_ids_with_few_guesses:
            unknown_photos.update(photos_set. \
                                      filter(confidence__lt=0.3,
                                             pk__in=photo_ids_with_few_guesses). \
                                      extra(**extra_args). \
                                      order_by('final_level')[:unknown_photos_to_get])

        if len(unknown_photos) < unknown_photos_to_get:
            unknown_photos.update(photos_set.exclude(
                pk__in=forbidden_photo_ids). \
                                      filter(confidence__lt=0.3). \
                                      extra(**extra_args). \
                                      order_by('final_level')[:(unknown_photos_to_get - \
                                                                len(unknown_photos))])

    if len(unknown_photos.union(known_photos)) < nr_of_photos:
        unknown_photos.update(photos_set. \
                                  extra(**extra_args). \
                                  order_by('?')[:unknown_photos_to_get])

    photos = list(unknown_photos.union(known_photos))
    photos = random.sample(photos, min(len(photos), nr_of_photos))

    data = []
    for p in photos:
        data.append({'id': p.id,
                     'description': p.description,  # 'date_text':p.date_text,
                     'source_key': p.source_key,
                     'big': _make_thumbnail(p, '700x400'),
                     'large': _make_fullscreen(p)
        })
    return data


# photod mille kohta saab anda feedbacki, ja mida ma
# pole viimase 24h jooksul arvanud
# photod millel on geotage, aga mille kohta ei saa veel
#			anda feedbacki, ja mida ma pole viimase 24h
#			jooksul arvanud; voi kui neid pole, siis
#			photod millel pole geotage ja mida on koige
#										vahem skipitud

def submit_guess(user, photo_id, lon=None, lat=None, type=GeoTag.MAP, hint_used=False, azimuth=None, zoom_level=None, azimuth_line_end_point=None, origin=GeoTag.GAME):
    p = Photo.objects.get(pk=photo_id)

    location_correct = False
    location_uncertain = False
    this_guess_score = 0
    azimuth_uncertain = False
    azimuth_correct = False
    feedback_message = ""

    if lon is not None and lat is not None:
        trustworthiness = calc_trustworthiness(user.pk)

        if origin == GeoTag.GAME:
            if p.confidence >= 0.3:
                error_in_meters = distance_in_meters(p.lon, p.lat, float(lon), float(lat))
                this_guess_score = int(130 * max(0, min(1, (1 - (error_in_meters - 15) / float(94 - 15)))))
                location_correct = (this_guess_score > 0)
            else:
                this_guess_score = max(20, int(300 * trustworthiness))
                if not p.lat and not p.lon:
                    location_uncertain = True
            if hint_used:
                this_guess_score *= 0.75
        else:
            this_guess_score = int(trustworthiness * 100)


        new_geotag = GeoTag(user=user, photo_id=p.id, type=type,
                            lat=float(lat), lon=float(lon),
                            is_correct=location_correct,
                            score=this_guess_score,
                            trustworthiness=trustworthiness,
                            zoom_level=zoom_level, origin=origin)

        if azimuth_line_end_point:
            new_geotag.azimuth_line_end_lat = azimuth_line_end_point[0]
            new_geotag.azimuth_line_end_lon = azimuth_line_end_point[1]

        if azimuth:
            new_geotag.azimuth = azimuth
            if not p.azimuth:
                if location_correct and origin == GeoTag.GAME:
                    new_geotag.azimuth_score = max(20, int(300 * trustworthiness))
                azimuth_uncertain = True

        if azimuth and p.azimuth:
            degree_error_point_array = [100, 99, 97, 93, 87, 83, 79, 73, 67, 61, 55, 46, 37, 28, 19, 10]
            azimuth = float(azimuth)
            difference = max(p.azimuth, azimuth) - min(p.azimuth, azimuth)
            if difference > 180:
                difference = 360 - difference
            azimuth_score = 0
            if int(difference) <= 15:
                azimuth_score = degree_error_point_array[int(difference)]
                azimuth_correct = True
            if azimuth_correct and (location_correct or location_uncertain) and origin == GeoTag.GAME:
                new_geotag.azimuth_score = azimuth_score

        if new_geotag.azimuth_score:
            new_geotag.score += new_geotag.azimuth_score
        new_geotag.save()
        new_action = Points(user=user, action=Points.GEOTAG, action_reference=new_geotag.id, points=new_geotag.score, created=datetime.datetime.now())
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
            if azimuth_uncertain:
                feedback_message = _("The location seems right, but the azimuth is yet uncertain.")
                if azimuth_tags_count == 1:
                    feedback_message = _("The location seems right, your azimuth was first.")
            elif not azimuth_correct:
                feedback_message = _("The location seems right, but not the azimuth.")
                if not azimuth:
                    feedback_message = _("The location seems right. Try submitting an azimuth to earn even more points!")
        elif location_uncertain:
            feedback_message = _("Correct location is not certain yet.")
        elif not location_correct:
            feedback_message = _("Other users have different opinion.")
        elif len(all_geotags_latlng_for_this_photo) == 1:
            feedback_message = _("Your guess was first.")

    return location_correct, location_uncertain, this_guess_score, feedback_message, all_geotags_latlng_for_this_photo, azimuth_tags_count, new_estimated_location, p.confidence


#
# DEPRICATED see models.Photo
#
def get_geotagged_photos(city_id=None):
    photos_set = Photo.objects.all()
    if city_id is not None:
        photos_set = photos_set.filter(city__pk=city_id)

    rephotographed_ids = photos_set.filter(
        rephoto_of__isnull=False).order_by(
        'rephoto_of').values_list(
        'rephoto_of', flat=True)
    rephotos = dict(zip(rephotographed_ids,
                        photos_set.filter(
                            rephoto_of__isnull=False).order_by(
                            'rephoto_of', 'id').distinct(
                            'rephoto_of').filter(
                            rephoto_of__in=rephotographed_ids)))
    data = []
    for p in photos_set.filter(confidence__gte=0.3,
                               lat__isnull=False, lon__isnull=False,
                               rephoto_of__isnull=True):
        r = rephotos.get(p.id)
        if r is not None and bool(r.image):
            im = get_thumbnail(r.image, '50x50', crop='center')
        else:
            im = get_thumbnail(p.image, '50x50', crop='center')
        data.append((p.id, im.url, p.lon, p.lat, p.id in rephotographed_ids))
    return data


def get_all_geotagged_photos(city_id=None):
    photos_set = Photo.objects.all()
    if city_id is not None:
        photos_set = photos_set.filter(city__pk=city_id)

    data = []
    for p in photos_set.filter(confidence__gte=0.3, lat__isnull=False, lon__isnull=False):
        data.append((p.lon, p.lat))
    return data


def get_all_geotag_submits(photo_id=None):
    geotag_set = GeoTag.objects.all()
    if photo_id is not None:
        geotag_set = geotag_set.filter(photo__pk=photo_id)

    data = []
    for g in geotag_set.filter(trustworthiness__gt=0.2):
        data.append((g.lon, g.lat))
    return data


def get_leaderboard(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_last_1000_geotags__gt=0) | Q(google_plus_name__isnull=False,
                                                                    score_last_1000_geotags__gt=0) | Q(
            pk=user_id)).values_list('pk', 'score_last_1000_geotags', 'fb_id', 'fb_name', 'google_plus_name',
                                     'google_plus_picture').order_by('-score_last_1000_geotags')))
    leaderboard = [scores_list[0]]
    self_user_idx = filter(lambda (idx, data): data[0] == user_id, scores_list)[0][0]
    if self_user_idx - 1 > 0:
        leaderboard.append(scores_list[self_user_idx - 1])
    if self_user_idx > 0:
        leaderboard.append(scores_list[self_user_idx])
    if self_user_idx + 1 < len(scores_list):
        leaderboard.append(scores_list[self_user_idx + 1])

    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3], data[4], data[5]) for idx, data in
                   leaderboard]
    return leaderboard


def get_leaderboard50(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_last_1000_geotags__gt=0) | Q(google_plus_name__isnull=False,
                                                                    score_last_1000_geotags__gt=0) | Q(pk=user_id)). \
                                     values_list('pk', 'score_last_1000_geotags', 'fb_id', 'fb_name',
                                                 'google_plus_name', 'google_plus_picture'). \
                                     order_by('-score_last_1000_geotags')))
    leaderboard = scores_list[:50]
    self_user_idx = filter(lambda (idx, data): data[0] == user_id,
                           scores_list)[0][0]

    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3]) \
                   for idx, data in leaderboard]
    return leaderboard


def get_rephoto_leaderboard(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_rephoto__gt=0) | Q(google_plus_name__isnull=False, score_rephoto__gt=0) | Q(
            pk=user_id)). \
                                     values_list('pk', 'score_rephoto', 'fb_id', 'fb_name', 'google_plus_name',
                                                 'google_plus_picture'). \
                                     order_by('-score_rephoto')))
    leaderboard = [scores_list[0]]
    self_user_idx = filter(lambda (idx, data): data[0] == user_id,
                           scores_list)[0][0]
    if self_user_idx - 1 > 0:
        leaderboard.append(scores_list[self_user_idx - 1])
    if self_user_idx > 0:
        leaderboard.append(scores_list[self_user_idx])
    if self_user_idx + 1 < len(scores_list):
        leaderboard.append(scores_list[self_user_idx + 1])

    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3], data[4], data[5]) \
                   for idx, data in leaderboard]
    return leaderboard


def get_rephoto_leaderboard50(user_id):
    scores_list = list(enumerate(Profile.objects.filter(
        Q(fb_name__isnull=False, score_rephoto__gt=0) | Q(google_plus_name__isnull=False, score_rephoto__gt=0) | Q(
            pk=user_id)). \
                                     values_list('pk', 'score_rephoto', 'fb_id', 'fb_name', 'google_plus_name',
                                                 'google_plus_picture'). \
                                     order_by('-score_rephoto')))
    leaderboard = scores_list[:50]
    self_user_idx = filter(lambda (idx, data): data[0] == user_id,
                           scores_list)[0][0]

    leaderboard = [(idx + 1, data[0] == user_id, data[1], data[2], data[3], data[4], data[5]) \
                   for idx, data in leaderboard]
    return leaderboard
