from datetime import datetime
from datetime import timezone
import urllib
import json
import os
import re
from django.forms.models import model_to_dict
from django.conf import settings


from django.core.management.base import BaseCommand

from ajapaik.ajapaik.muis_utils import add_dating_to_photo, add_person_albums, add_geotag_from_address_to_photo, \
    extract_dating_from_event, get_muis_date_and_prefix, set_text_fields_from_muis, reset_modeltranslated_field
from ajapaik.ajapaik.models import Album, AlbumPhoto, Dating, Photo, ApplicationException
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Update photo directory from ./media/uploads to ./media/uploads/YYYY/MM'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT + '/'
        if 1:
            print("Remove exit from start of the script if you want really execute this")
            exit(1)
        photos = Photo.objects.values('id','image', 'created', 'uploader_is_author', 'rephoto_of_id')
#        photos = Photo.objects.all()[:5]
        for photo in photos:
            try:
                m = re.search(r'uploads/.*?/', photo['image'])
                if m==None:
                   print(photo)
                   year=photo['created'].strftime("%Y")
                   month=photo['created'].strftime("%m")
                   day=photo['created'].strftime("%d")

                   # Photo is rephoto
                   if photo['rephoto_of_id']!=None and photo['rephoto_of_id']>0:
                      upload_dir='uploads/r'

                      # Create /r directory
                      newDirName=media_root + upload_dir
                      if not os.path.exists(newDirName):
                         os.mkdir(newDirName)
                         print("directory " + newDirName + " created")

                   # Own photo
                   elif photo['uploader_is_author']==True:
                      upload_dir='uploads/u'

                      # Create /u directory
                      newDirName=media_root + upload_dir
                      if not os.path.exists(newDirName):
                         os.mkdir(newDirName)
                         print("directory " + newDirName + " created")

                   else:
                      upload_dir='uploads'

                   # Create year directory
                   newDirName=media_root + upload_dir + '/' + year
                   if not os.path.exists(newDirName):
                      os.mkdir(newDirName)
                      print("directory " + newDirName + " created")

                   # Create month directory
                   newDirName=media_root + upload_dir + '/' + year + '/' +month
                   if not os.path.exists(newDirName):
                      os.mkdir(newDirName)
                      print("directory " + newDirName + " created")

                   # Create day directory
                   newDirName=media_root + upload_dir + '/' + year + '/' +month + '/' +day
                   if not os.path.exists(newDirName):
                      os.mkdir(newDirName)
                      print("directory " + newDirName + " created")

                   newImagePath=upload_dir +'/' + year + '/' + month + '/' + day + '/'
                   newImageName=photo['image'].replace('uploads/', newImagePath)

                   origImageFullPath=media_root + photo["image"]
                   newImageFullPath=media_root + newImageName
                   if not os.path.exists(newImageFullPath):
                      print("Moving " + photo["image"] + " to " + newImageName)
                      p=Photo.objects.get(pk=photo["id"])
                      os.rename(origImageFullPath, newImageFullPath)
                      p.image=newImageName
                      p.save()
                   else:
                      print("ERROR: " + newImageFullPath + " already exists! exiting...")

#                   print(newImageName)
                   photo=Photo.objects.values('id','image', 'created', 'uploader_is_author').get(pk=photo["id"])
                   if photo["image"] != newImageName:
                      print(photo)
                      print(newImageName)
                      exit("Updated filenames doesn't match")
                else:
                   continue
#                exit(1)
            except Exception as e:
                print(e)
                exit(1)

