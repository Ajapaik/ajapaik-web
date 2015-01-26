from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Will copy over profiles from backup"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO project_profile SELECT profile.user_id, profile.fb_name, profile.fb_link, profile.fb_id, profile.fb_token, profile.fb_hometown, profile.fb_current_location, profile.fb_birthday, profile.fb_email, profile.fb_user_friends, profile.google_plus_id, profile.google_plus_link, profile.google_plus_name, profile.google_plus_token, profile.google_plus_picture, profile.avatar_url, profile.modified, profile.score, profile.score_rephoto, profile.score_last_1000_geotags FROM dblink('dbname=rephoto_backup user=rephoto password=reph0t0sqluser', 'SELECT fb_id, fb_token, avatar_url, modified, user_id, fb_name, fb_link, score, score_rephoto, google_plus_id, google_plus_link, google_plus_name, google_plus_token, google_plus_picture, fb_hometown, fb_current_location, fb_birthday, fb_email, fb_user_friends, score_last_1000_geotags FROM project_profile')
    AS profile(fb_id VARCHAR(100), fb_token VARCHAR(511), avatar_url VARCHAR(200), modified TIMESTAMP, user_id integer, fb_name VARCHAR(255), fb_link VARCHAR(255), score integer, score_rephoto integer, google_plus_id VARCHAR(100), google_plus_link VARCHAR(255), google_plus_name VARCHAR(255), google_plus_token VARCHAR(255), google_plus_picture VARCHAR(255), fb_hometown VARCHAR(511), fb_current_location VARCHAR(511), fb_birthday DATE, fb_email VARCHAR(255), fb_user_friends VARCHAR, score_last_1000_geotags INTEGER);''')