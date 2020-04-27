import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import ConnectionDoesNotExist

from ajapaik.ajapaik.models import Photo, Licence, Profile, Source, Device, \
    Area, Video


class Command(BaseCommand):
    help = ('Transfers rephotos from staging to production. As arguments takes '
            'photos id list from staging. This command must be run from '
            'staging environment. This script require production database to '
            'be configured in DATABASES["production"].\n'
            'Usage: manage.py clone_rephoto photo_id_1 photo_id_2 photo_id_3'
            'Example: manage.py clone_rephoto 123 456 789')

    def add_arguments(self, parser):
        parser.add_argument(
            'photo_ids', nargs='+', type=int, help='photo ids for cloning'
        )

    def handle(self, *args, **options):
        '''
            Get rephoto for given IDs and replace relation sensative data with
            data from production DB. Then creates new rephoto in production DB
            with actual IDs.
        '''
        for photo_id in options['photo_ids']:
            rephotos = Photo.objects.filter(rephoto_of=photo_id)
            if not rephotos:
                self.stderr.write(
                    'Photo with ID: {} have no rephotos.'.format(photo_id)
                )
                continue
            rephotos_values = rephotos.values()
            for i, rephoto in enumerate(rephotos):
                try:
                    production_photo = Photo.objects.using('production').get(
                        image=rephoto.rephoto_of.image
                    )
                except ConnectionDoesNotExist:
                    raise CommandError(
                        'This script require production database to be '
                        'configured in DATABASES["production"].'
                    )
                rephoto_data = rephotos_values[i]
                rephoto_data['id'] = None

                production_license = None
                if rephoto.licence:
                    try:
                        production_license = Licence.objects.using('production') \
                            .get(name=rephoto.licence.name).id
                    except Licence.DoesNotExist:
                        pass
                rephoto_data['licence_id'] = production_license

                try:
                    production_user = Profile.objects.using('production') \
                        .get(user__username=rephoto.user.user.get_username ).id
                except Profile.DoesNotExist:
                    production_user = None
                rephoto_data['user_id'] = production_user

                production_source = None
                if rephoto.source:
                    try:
                        production_source = Source.objects.using('production') \
                            .get(name=rephoto.source.name).id
                    except Licence.DoesNotExist:
                        pass

                rephoto_data['source_id'] = production_source

                production_device = None
                if rephoto.device:
                    try:
                        production_device = Device.objects.using('production') \
                            .get(
                                camera_make=rephoto.device.camera_make,
                                camera_model=rephoto.device.camera_model,
                                lens_make=rephoto.device.lens_make,
                                lens_model=rephoto.device.lens_model,
                                software=rephoto.device.software
                            ).id
                    except Device.DoesNotExist:
                        pass
                rephoto_data['device_id'] = production_device

                production_area = None
                if rephoto.area:
                    try:
                        production_area = Area.objects.using('production') \
                            .get(name=rephoto.area.name).id
                    except Licence.DoesNotExist:
                        pass
                rephoto_data['area_id'] = production_area

                production_video = None
                if rephoto.video:
                    try:
                        production_video = Video.objects.using('production') \
                            .get(file=rephoto.video.file).id
                    except Licence.DoesNotExist:
                        pass
                rephoto_data['video_id'] = production_video

                rephoto_data['image'] = rephoto.image
                rephoto_data['image_unscaled'] = rephoto.image_unscaled
                rephoto_data['image_no_watermark'] = rephoto.image_no_watermark
                rephoto_data['rephoto_of_id'] = production_photo.id

                Photo.objects.using('production').create(**rephoto_data)
