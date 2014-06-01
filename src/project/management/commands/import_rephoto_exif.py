import re
from django.core.management.base import BaseCommand,CommandError
from django.core.exceptions import ObjectDoesNotExist
from project.models import *
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from PIL.ExifTags import TAGS, GPSTAGS
from time import gmtime, strftime, strptime

def _convert_to_degress(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)
    
def _get_exif_data(img):
    try:
        exif = img._getexif()
    except (AttributeError, IOError, KeyError, IndexError):
        exif = None
    if (exif is None):
        return None

    exif_data = {}
    for (tag, value) in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                exif_data[decoded+'.'+sub_decoded] = value[t]

        elif (len(str(value)) < 50):
            exif_data[decoded] = value
        else:
            exif_data[decoded] = None
            
    return exif_data

class Command(BaseCommand):
    args='photo_id'
    help='imports EXIF meta data'

    def handle(self,*args,**options):
        args=list(args)
        photo_id = None
        if len(args):
            photo_id=args.pop(0)

        if photo_id:
            photos_without_meta = Photo.objects.filter(rephoto_of__isnull=False, pk=photo_id)[:1]
        else:
            photos_without_meta = Photo.objects.filter(rephoto_of__isnull=False, device__isnull=True)

        for photo in photos_without_meta:
            img = Image.open('/var/garage/' + str(photo.image))
            if (img is None):
                print >>self.stdout, (photo.id, 'image missing')
                continue

            exif_data = _get_exif_data(img)
            if (exif_data is None):
                print >>self.stdout, (photo.id, 'exif missing')
                continue
                
            # print >>self.stdout, (photo.id, exif_data)
            # continue

            if ((photo.lat is None or photo.lon is None) and ('GPSInfo.GPSLatitudeRef' in exif_data and 'GPSInfo.GPSLatitude' in exif_data and 'GPSInfo.GPSLongitudeRef' in exif_data and 'GPSInfo.GPSLongitude' in exif_data)):
                gps_latitude_ref = exif_data.get('GPSInfo.GPSLatitudeRef')
                gps_latitude = exif_data.get('GPSInfo.GPSLatitude')
                gps_longitude_ref = exif_data.get('GPSInfo.GPSLongitudeRef')
                gps_longitude = exif_data.get('GPSInfo.GPSLongitude')

                lat = _convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat

                lon = _convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon

                photo.lat = lat
                photo.lon = lon
                photo.save()
                print >>self.stdout, (photo.id, 'gpsinfo updated')

            if (photo.device is None and ('Make' in exif_data or 'Model' in exif_data or 'LensMake' in exif_data or 'LensModel' in exif_data or 'Software' in exif_data)):
                camera_make = exif_data.get('Make')
                camera_model = exif_data.get('Model')
                lens_make = exif_data.get('LensMake')
                lens_model = exif_data.get('LensModel')
                software = exif_data.get('Software')
                try:
                    device=Device.objects.get(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make, lens_model=lens_model, software=software)
                except ObjectDoesNotExist:
                    device=Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make, lens_model=lens_model, software=software)
                    device.save()

                photo.device = device
                photo.save()
                print >>self.stdout, (photo.id, 'device updated')

            if (photo.date is None and 'DateTimeOriginal' in exif_data):
                date_taken = exif_data.get('DateTimeOriginal')
                try:
                    parsed_time = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                except (ValueError):
                    parsed_time = None
                if (parsed_time):
                    parsed_time = strftime("%H:%M:%S", parsed_time)

                # ignore default camera dates
                if (parsed_time and parsed_time != '12:00:00' and parsed_time != '00:00:00'):
                    try:
                        parsed_date = strptime(date_taken, "%Y:%m:%d %H:%M:%S")
                    except (ValueError):
                        parsed_date = None
                    if (parsed_date):
                        photo.date = strftime("%Y-%m-%d", parsed_date)
                    photo.save()
                    print >>self.stdout, (photo.id, 'taken date updated')

        #print >>self.stdout, (Image.VERSION)
