import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from ajapaik.ajapaik.models import Photo


class Command(BaseCommand):
    help = 'Update photo directory from ./media/uploads to ./media/uploads/YYYY/MM'

    def handle(self, *args, **options):
        media_root = f'{settings.MEDIA_ROOT}/'
        if 1:
            print("Remove exit from start of the script if you want really execute this")
            exit(1)
        photos = Photo.objects.values('id', 'image', 'created', 'uploader_is_author', 'rephoto_of_id')
#       photos = Photo.objects.all()[:5]
        for photo in photos:
            try:
                m = re.search(r'uploads/.*?/', photo['image'])
                if m is None:
                    print(photo)
                    year = photo['created'].strftime("%Y")
                    month = photo['created'].strftime("%m")
                    day = photo['created'].strftime("%d")

                    # Photo is rephoto
                    if photo['rephoto_of_id'] is None and photo['rephoto_of_id'] > 0:
                        upload_dir = 'uploads/r'

                        # Create /r directory
                        new_dir_name = f'{media_root}{upload_dir}'
                        if not os.path.exists(new_dir_name):
                            os.mkdir(new_dir_name)
                            print(f'directory {new_dir_name} created')

                    # Own photo
                    elif photo['uploader_is_author'] is True:
                        upload_dir = 'uploads/u'

                        # Create /u directory
                        new_dir_name = f'{media_root}{upload_dir}'
                        if not os.path.exists(new_dir_name):
                            os.mkdir(new_dir_name)
                            print(f'directory {new_dir_name} created')

                    else:
                        upload_dir = 'uploads'

                    # Create year directory
                    new_dir_name = f'{media_root}{upload_dir}/{year}'
                    if not os.path.exists(new_dir_name):
                        os.mkdir(new_dir_name)
                        print(f'directory {new_dir_name} created')

                    # Create month directory
                    new_dir_name = f'{media_root}{upload_dir}/{year}/{month}'
                    if not os.path.exists(new_dir_name):
                        os.mkdir(new_dir_name)
                        print(f'directory {new_dir_name} created')

                    # Create day directory
                    new_dir_name = f'{media_root}{upload_dir}/{year}/{month}/{day}'
                    if not os.path.exists(new_dir_name):
                        os.mkdir(new_dir_name)
                        print(f'directory {new_dir_name} created')

                    new_img_path = f'{upload_dir}/{year}/{month}/{day}/'
                    new_img_name = photo['image'].replace('uploads/', new_img_path)

                    orig_img_full_path = f'{media_root}{photo["image"]}'
                    new_img_full_path = f'{media_root}{new_img_name}'
                    if not os.path.exists(new_img_full_path):
                        print(f'Moving {photo["image"]} to {new_img_name}')
                        p = Photo.objects.get(pk=photo["id"])
                        os.rename(orig_img_full_path, new_img_full_path)
                        p.image = new_img_name
                        p.save()
                    else:
                        print(f'ERROR: {new_img_full_path} already exists! exiting...')

                    photo = Photo.objects.values('id', 'image', 'created', 'uploader_is_author').get(pk=photo["id"])
                    if photo["image"] != new_img_name:
                        print(photo)
                        print(new_img_name)
                        exit("Updated filenames doesn't match")
                else:
                    continue
#                exit(1)
            except Exception as e:
                print(e)
                exit(1)
