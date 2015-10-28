import os.path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image, ImageFile
from project.ajapaik.models import Photo

ImageFile.LOAD_TRUNCATED_IMAGES = True
from StringIO import StringIO
from copy import deepcopy


# Old command, now idea if/how it works
class Command(BaseCommand):
    args='photo_id'
    help='scales photos by cam_scale_factor'

    def handle(self,*args,**options):
        args=list(args)
        photo_id = None
        if len(args):
            photo_id=args.pop(0)

        if photo_id:
            scaleable_photos = Photo.objects.filter(rephoto_of__isnull=False, image_unscaled__isnull=True, cam_scale_factor__isnull=False, pk=photo_id).exclude(cam_scale_factor=1)[:1]
        else:
            scaleable_photos = Photo.objects.filter(rephoto_of__isnull=False, image_unscaled__isnull=True, cam_scale_factor__isnull=False).exclude(cam_scale_factor=1)[:10]

        for photo in scaleable_photos:
            file_key=os.path.basename(str(photo.image))
            img = Image.open('/var/garage/' + str(photo.image))
            if (img is None):
                print >>self.stdout, (photo.id, 'image missing')
                continue

            new_size = tuple([int(x*photo.cam_scale_factor) for x in img.size])
            output_file = StringIO()

            if (photo.cam_scale_factor < 1):
                x0 = (img.size[0]-new_size[0])/2;
                y0 = (img.size[1]-new_size[1])/2;
                x1 = img.size[0]-x0;
                y1 = img.size[1]-y0;
                new_img = img.transform(new_size, Image.EXTENT, (x0, y0, x1, y1))
                new_img.save(output_file, 'JPEG', quality=95)
                photo.image_unscaled = deepcopy(photo.image)
                photo.image.save(file_key, ContentFile(output_file.getvalue()))
            elif (photo.cam_scale_factor > 1):
                x0 = (new_size[0]-img.size[0])/2;
                y0 = (new_size[1]-img.size[1])/2;
                new_img = Image.new("RGB", new_size)
                new_img.paste(img, (x0, y0))
                new_img.save(output_file, 'JPEG', quality=95)
                photo.image_unscaled = deepcopy(photo.image)
                photo.image.save(file_key, ContentFile(output_file.getvalue()))

            print >>self.stdout, (photo.id, file_key, photo.cam_scale_factor, img.size, new_size)

        #print >>self.stdout, (Image.VERSION)
