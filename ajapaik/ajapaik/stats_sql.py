from django.db import connection

from ajapaik.ajapaik.models import AlbumPhoto, Profile


# Direct SQL queries for settings stats with reasonably speed. If possible, rewrite using Django ORM

# AlbumStats is used in views.get_album_info_modal_content()
class AlbumStats():

    # Return number of geotagged photos in albums by user
    def get_user_geotagged_photo_count_sql(albums, user_id):
        albums_str = ",".join(map(str, map(int, albums)))
        ret = 0

        if user_id and albums_str and user_id > 0:
            user_id_str = str(int(user_id))
            sql = "SELECT count(distinct(g.photo_id)) as user_geotagged_photo_count"
            sql = sql + " FROM project_albumphoto as ap, project_geotag as g"
            sql = sql + " WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id AND g.user_id=" + user_id_str

            cursor = connection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            ret = row[0] or 0

        return ret

    # Return number of users who geotagged photos in albums
    def get_geotagging_user_count_sql(albums):
        albums_str = ",".join(map(str, map(int, albums)))
        ret = 0
        if albums:
            sql = "SELECT count(distinct(g.user_id)) as geotagging_user_count ";
            sql = sql + " FROM project_albumphoto as ap, project_geotag as g ";
            sql = sql + " WHERE ap.album_id IN (" + albums_str + ") AND g.photo_id=ap.photo_id"
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
    def get_rephoto_stats_sql(albums, user_id):
        albums_str = ",".join(map(str, map(int, albums)))

        ret = {}
        ret['user_rephotographed_photo_count'] = 0
        ret['user_rephoto_count'] = 0
        ret['rephoto_user_count'] = 0
        ret['rephotographed_photo_count'] = 0
        ret['rephoto_count'] = 0
        ret['user_made_all_rephotos'] = False
        if albums_str and user_id and user_id > 0:
            user_id_str = str(int(user_id))
            sql = "SELECT COUNT(DISTINCT(CASE WHEN p2.user_id=" + user_id_str + " THEN  p2.rephoto_of_id ELSE NULL END )) AS user_rephotographed_photo_count, "
            sql = sql + " COUNT(DISTINCT(CASE WHEN p2.user_id=" + user_id_str + " THEN  p2.id ELSE NULL END )) AS user_rephoto_count, "
            sql = sql + " COUNT(DISTINCT(p2.user_id)) AS rephoto_user_count, "
            sql = sql + " COUNT(DISTINCT(p1.id))  AS rephotographed_photo_count, "
            sql = sql + " COUNT(DISTINCT(p2.id))  AS rephoto_count "
            sql = sql + " FROM project_albumphoto AS ap, project_photo AS p1, project_photo AS p2 "
            sql = sql + " WHERE "
            sql = sql + " ap.album_id IN (" + albums_str + ") "
            sql = sql + " AND p1.id=ap.photo_id ";
            sql = sql + " AND p2.rephoto_of_id=p1.id"
            cursor = connection.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            ret = dict(zip(columns, row))
            ret['user_made_all_rephotos'] = (ret['rephoto_user_count'] == 1) and (
                    ret['user_rephoto_count'] == ret['rephoto_count'])
            print(ret)
        return ret

    # List of users who added photos to album

    def get_album_curators_sql(albums):
        albums_str = ",".join(map(str, map(int, albums)))

        album_types = [AlbumPhoto.UPLOADED, AlbumPhoto.CURATED, AlbumPhoto.RECURATED]
        album_types_str = ",".join(map(str, album_types))
        ret = []
        if albums_str:
            sql = "SELECT pp.user_id ";
            sql = sql + " FROM project_profile as pp, project_albumphoto as ap ";
            sql = sql + " WHERE ap.type IN (" + album_types_str + ") ";
            sql = sql + " AND ap.album_id IN (" + albums_str + ") ";
            sql = sql + " AND ap.profile_id=pp.user_id ";
            sql = sql + " GROUP BY pp.user_id ";
            sql = sql + " ORDER BY sum(1) DESC"

            profiles = Profile.objects.raw(sql)
            for profile in profiles:
                ret.append(profile)

        return ret

class GlobalStats():
    @staticmethod
    def get_global_stats_sql():
        from ajapaik.ajapaik.models import Photo, GeoTag
        from ajapaik.ajapaik_face_recognition.models import FaceRecognitionRectangle

        cursor = connection.cursor()

        # 1. Photo stats
        # We respect the same filters as Photo.objects (soft_deleted=False and specific source_key exclusions)
        photo_table = Photo._meta.db_table
        sql_photo = f"""
            SELECT
                COUNT(CASE WHEN rephoto_of_id IS NULL AND NOT soft_deleted AND (source_key IS NULL OR (source_key NOT LIKE 'ERM Fk 2903%' AND source_key NOT LIKE 'TLM F 10198:%')) THEN 1 END) as photos_count,
                COUNT(CASE WHEN rephoto_of_id IS NULL AND NOT soft_deleted AND (source_key IS NULL OR (source_key NOT LIKE 'ERM Fk 2903%' AND source_key NOT LIKE 'TLM F 10198:%')) AND lat IS NOT NULL AND lon IS NOT NULL THEN 1 END) as photos_geotagged_count,
                COUNT(CASE WHEN rephoto_of_id IS NOT NULL THEN 1 END) as rephotos_count,
                COUNT(DISTINCT CASE WHEN rephoto_of_id IS NOT NULL THEN user_id END) as rephotographing_users_count,
                COUNT(DISTINCT CASE WHEN rephoto_of_id IS NOT NULL THEN rephoto_of_id END) as photos_with_rephotos_count
            FROM {photo_table};
        """
        cursor.execute(sql_photo)
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        res = dict(zip(columns, row))

        # 2. GeoTag stats
        geotag_table = GeoTag._meta.db_table
        sql_geotag = f"SELECT COUNT(DISTINCT user_id) FROM {geotag_table}"
        cursor.execute(sql_geotag)
        res['contributing_users_count'] = cursor.fetchone()[0]

        # 3. Face recognition stats
        fr_table = FaceRecognitionRectangle._meta.db_table
        sql_fr = f"""
            SELECT
                COUNT(*) as person_annotation_count,
                COUNT(CASE WHEN subject_consensus_id IS NOT NULL THEN 1 END) as person_annotation_count_with_person_album,
                COUNT(CASE WHEN gender IS NOT NULL OR age IS NOT NULL THEN 1 END) as person_annotation_count_with_subject_data
            FROM {fr_table}
            WHERE deleted IS NULL
        """
        cursor.execute(sql_fr)
        row = cursor.fetchone()
        res['person_annotation_count'] = row[0]
        res['person_annotation_count_with_person_album'] = row[1]
        res['person_annotation_count_with_subject_data'] = row[2]

        return res
