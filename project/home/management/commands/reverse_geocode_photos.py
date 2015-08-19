# -*- coding: utf-8 -*-
from time import sleep
from django.core.management.base import BaseCommand
from requests import get
from project.home.models import Photo, GoogleMapsReverseGeocode
from project.settings import GOOGLE_API_KEY
from ujson import loads


class Command(BaseCommand):
    help = 'Will try to reverse geocode all photos that have no address yet'

    def handle(self, *args, **options):
        url_template = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%0.5f,%0.5f&key=' + GOOGLE_API_KEY
        # FIXME: Get only one for testing
        photos = Photo.objects.filter(rephoto_of__isnull=True, address__isnull=True)
        for p in photos:
            if p.lat and p.lon:
                lat = p.lat
                lon = p.lon
            elif p.albums:
                for a in p.albums.all():
                    if a.lat and a.lon:
                        lat = a.lat
                        lon = a.lon
                        break
            if lat and lon:
                cached_response = GoogleMapsReverseGeocode.objects.filter(lat='{:.5f}'.format(lat),
                                                                          lon='{:.5f}'.format(lon)).first()
                if cached_response:
                    response = cached_response.response
                else:
                    sleep(0.2)
                    response = get(url_template % (lat, lon))
                    decoded_response = loads(response.text)
                    if decoded_response['status'] == 'OK' or decoded_response['status'] == 'ZERO_RESULTS':
                        GoogleMapsReverseGeocode(
                            lat='{:.5f}'.format(lat),
                            lon='{:.5f}'.format(lon),
                            response=response.text
                        ).save()
                    response = decoded_response
                if response['status'] == 'OK':
                    most_accurate_result = response['results'][0]
                    p.address = most_accurate_result['formatted_address']
                    p.light_save()
                elif response['status'] == 'OVER_QUERY_LIMIT':
                    return