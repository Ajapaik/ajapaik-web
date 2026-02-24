from time import strptime, strftime

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from ajapaik.ajapaik.models import Device
from ajapaik.utils import convert_to_degrees


def _get_exif_data(img):
    try:
        exif = img._getexif()
    except (AttributeError, IOError, KeyError, IndexError):
        exif = None
    if exif is None:
        return None
    exif_data = {}
    for (tag, value) in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == 'GPSInfo':
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                exif_data[f'{str(decoded)}.{str(sub_decoded)}'] = value[t]
        elif len(str(value)) < 50:
            exif_data[decoded] = value
        else:
            exif_data[decoded] = None

    return exif_data


def _extract_and_save_data_from_exif(photo_with_exif):
    img = Image.open(f'{settings.MEDIA_ROOT}/{str(photo_with_exif.image)}')
    exif_data = _get_exif_data(img)
    if exif_data:
        if 'GPSInfo.GPSLatitudeRef' in exif_data and 'GPSInfo.GPSLatitude' in exif_data and 'GPSInfo.GPSLongitudeRef' \
                in exif_data and 'GPSInfo.GPSLongitude' in exif_data:
            gps_latitude_ref = exif_data.get('GPSInfo.GPSLatitudeRef')
            gps_latitude = exif_data.get('GPSInfo.GPSLatitude')
            gps_longitude_ref = exif_data.get('GPSInfo.GPSLongitudeRef')
            gps_longitude = exif_data.get('GPSInfo.GPSLongitude')
            try:
                lat = convert_to_degrees(gps_latitude)
                if gps_latitude_ref != 'N':
                    lat = 0 - lat
                lon = convert_to_degrees(gps_longitude)
                if gps_longitude_ref != 'E':
                    lon = 0 - lon
                photo_with_exif.lat = lat
                photo_with_exif.lon = lon
                photo_with_exif.save()
            except:
                print("convert_to_degrees() failed")

        if 'Make' in exif_data or 'Model' in exif_data or 'LensMake' in exif_data or 'LensModel' in exif_data \
                or 'Software' in exif_data:
            camera_make = exif_data.get('Make')
            camera_model = exif_data.get('Model')
            lens_make = exif_data.get('LensMake')
            lens_model = exif_data.get('LensModel')
            software = exif_data.get('Software')
            try:
                device = Device.objects.get(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make,
                                            lens_model=lens_model, software=software)
            except ObjectDoesNotExist:
                try:
                    device = Device(camera_make=camera_make, camera_model=camera_model, lens_make=lens_make,
                                    lens_model=lens_model, software=software)
                    device.save()
                except:  # noqa
                    device = None
            photo_with_exif.device = device
            photo_with_exif.save()
        if 'DateTimeOriginal' in exif_data and not photo_with_exif.date:
            date_taken = exif_data.get('DateTimeOriginal')
            try:
                parsed_time = strptime(date_taken, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                parsed_time = None
            if parsed_time:
                parsed_time = strftime('%H:%M:%S', parsed_time)
            # ignore default camera dates
            if parsed_time and parsed_time != '12:00:00' and parsed_time != '00:00:00':
                try:
                    parsed_date = strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    parsed_date = None
                if parsed_date:
                    photo_with_exif.date = strftime('%Y-%m-%d', parsed_date)
                    photo_with_exif.save()
        return True
    else:
        return False
