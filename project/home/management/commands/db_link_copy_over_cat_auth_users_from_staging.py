from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Will copy over categorizer auth credentials from staging"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO auth_user SELECT p.username, p.password FROM dblink('dbname=rephoto_dev user=rephoto password=reph0t0sqluser', 'SELECT username, password FROM auth_user WHERE id IN =(20081,20065,19933,19997,19999,19943,19940,19946,19947,20075,19921,19937,19998,20074,19936,20062,20060,20061,18585,19935,19941,20047,19883,20087,19944,20008,20005,19932,19925,20006,20077,19939,20000,20059,19922,20080,19996,19934,19942,19954,19923,19926,20088,20003,20067,20009,19929)')
    AS p(username VARCHAR(30), password VARCHAR(128));''')