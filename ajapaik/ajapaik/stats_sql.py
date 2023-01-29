from typing import Union

from django.db import connection

from ajapaik.ajapaik.models import AlbumPhoto, Profile


# Direct SQL queries for getting stats with reasonably speed. If possible, rewrite using Django ORM

# AlbumStats is used in views.get_album_info_modal_content()

# Return number of geotagged photos in albums by user
def get_user_geotagged_photo_count_sql(album_ids: list[int], user_id: int):
    album_ids_str = ','.join([str(album_id) for album_id in album_ids])
    ret = 0

    if album_ids_str and user_id > 0:
        sql = "SELECT count(distinct(g.photo_id)) as user_geotagged_photo_count FROM project_albumphoto as ap," + \
              "project_geotag as g WHERE ap.album_id IN " + \
              f"({album_ids_str}) AND g.photo_id=ap.photo_id AND g.user_id={user_id}"

        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        ret = row[0] or 0

    return ret


# Return number of users who geotagged photos in albums
def get_geotagging_user_count_sql(album_ids: list[int]):
    album_ids_str = ','.join([str(album_id) for album_id in album_ids])
    ret = 0
    if album_ids_str:
        sql = f"SELECT count(distinct(g.user_id)) as geotagging_user_count FROM project_albumphoto as ap, project_geotag as g  WHERE ap.album_id IN ({album_ids_str}) AND g.photo_id=ap.photo_id"
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        ret = row[0] or 0
    return ret


# Return various rephotography stats of photos in albums
# Number of rephotographed photos by user
# Number of rephotos by user
# Number of users with rephotos
# Number of rephotographed photos by all users
# Number of rephotos by all users
def get_rephoto_stats_sql(album_ids: list[int], user_id: int) -> dict[str, Union[str, bool]]:
    album_ids_str = ','.join([str(album_id) for album_id in album_ids])

    ret = {'user_rephotographed_photo_count': 0, "user_rephoto_count": 0, "rephoto_user_count": 0,
           "rephotographed_photo_count": 0, "rephoto_count": 0, "user_made_all_rephotos": False}
    if album_ids_str and user_id > 0:
        sql = f"SELECT COUNT(DISTINCT(CASE WHEN p2.user_id={user_id} THEN  p2.rephoto_of_id ELSE NULL END )) AS user_rephotographed_photo_count, "
        sql = sql + f" COUNT(DISTINCT(CASE WHEN p2.user_id={user_id} THEN  p2.id ELSE NULL END )) AS user_rephoto_count, "
        sql = sql + " COUNT(DISTINCT(p2.user_id)) AS rephoto_user_count, "
        sql = sql + " COUNT(DISTINCT(p1.id))  AS rephotographed_photo_count, "
        sql = sql + " COUNT(DISTINCT(p2.id))  AS rephoto_count "
        sql = sql + " FROM project_albumphoto AS ap, project_photo AS p1, project_photo AS p2 "
        sql = sql + " WHERE "
        sql = sql + f"ap.album_id IN ({album_ids_str}) "
        sql = sql + " AND p1.id=ap.photo_id "
        sql = sql + " AND p2.rephoto_of_id=p1.id"
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        ret = dict(zip(columns, row))
        ret['user_made_all_rephotos'] = ret['rephoto_user_count'] == 1 and ret['user_rephoto_count'] == ret[
            'rephoto_count']
    return ret


# List of users who added photos to album

def get_album_curators_sql(album_ids: list[int]) -> list[int]:
    album_ids_str = ','.join([str(album_id) for album_id in album_ids])

    album_types = [AlbumPhoto.UPLOADED, AlbumPhoto.CURATED, AlbumPhoto.RECURATED]
    album_types_str = ','.join([str(album_type) for album_type in album_types])

    if album_ids_str:
        sql = "SELECT pp.user_id "
        sql = sql + " FROM project_profile as pp, project_albumphoto as ap "
        sql = sql + f" WHERE ap.type IN ({album_types_str}) "
        sql = sql + f" AND ap.album_id IN ({album_ids_str}) "
        sql = sql + " AND ap.profile_id=pp.user_id "
        sql = sql + " GROUP BY pp.user_id "
        sql = sql + " ORDER BY sum(1) DESC"

        profiles = Profile.objects.raw(sql)
        return profiles

    return []
