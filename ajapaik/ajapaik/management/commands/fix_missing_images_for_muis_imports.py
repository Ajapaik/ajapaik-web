import logging
import traceback
import urllib
import xml.etree.ElementTree as ET

import requests
from django.core.management.base import BaseCommand

from ajapaik import settings
from ajapaik.ajapaik.models import Photo, ApplicationException

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import photos from MUIS set'

    def add_arguments(self, parser):
        parser.add_argument(
            'photo_ids', nargs='?', type=int,
            help='Photo ids, where to import the photos from muis'
        )
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        photo_ids = options.get('photo_ids')
        force = options.get('force')
        photos = None

        if photo_ids:
            photos = Photo.objects.filter(id__in=photo_ids, rephoto_of=None, back_of_id=None,
                                          external_id__startswith='oai:muis.ee')
        elif force:
            photos = Photo.objects.filter(rephoto_of=None, back_of_id=None, width=None, height=None,
                                          external_id__startswith='oai:muis.ee')
        else:
            logger.info("Please add photo ids that you want to update")

        if not photos:
            logger.info("No photos found to update")

        muis_url = 'https://www.muis.ee/OAIService/OAIService'
        for photo in photos:
            logger.info('Running update for: {photo.id}')
            list_identifiers_url = f'{muis_url}?verb=GetRecord&identifier={photo.external_id}&metadataPrefix=lido'
            url_response = urllib.request.urlopen(list_identifiers_url)

            ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}
            record = 'd:metadata/lido:lidoWrap/lido:lido/'
            resource_wrap = f'{record}lido:administrativeMetadata/lido:resourceWrap/'

            read_url = url_response.read()
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.fromstring(read_url, parser=parser)
            rec = tree.find('d:GetRecord/d:record', ns)

            try:
                rp_lr = 'resourceRepresentation/lido:linkResource'
                link_resource_record = rec.find(f'{resource_wrap}lido:resourceSet/lido:{rp_lr}', ns)

                if not photo.external_id.startswith('oai:muis.ee'):
                    logger.info(f'Skipping, not a muis photo, {photo.id} ({photo.external_id})')

                if link_resource_record is None:
                    logger.info(f"Skipping {photo.id} ({photo.external_id}), as there is no image resource")
                    continue

                image_url = link_resource_record.text

                if link_resource_record is None:
                    logger.info(f"Skipping {photo.id} ({photo.external_id}), as there is not image extension specified")
                    continue

                image_extension = (link_resource_record.attrib['{' + ns['lido'] + '}formatResource']).lower()

                if not image_url or image_extension not in ['gif', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp']:
                    logger.info(
                        f"Skipping {photo.id} ({photo.external_id}), as there are no photos which are supported")
                    continue

                response = requests.get(image_url)
                if response.status_code != 200:
                    logger.info(
                        f"Skipping {photo.id} ({photo.external_id}), as we did not get a valid response when downloading")
                    continue

                img_data = response.content

                MEDIA_ROOT = settings.MEDIA_ROOT
                with open(f'{MEDIA_ROOT}/{photo.image.name}', 'wb') as handler:
                    handler.write(img_data)

                logger.info(f'{MEDIA_ROOT}/{photo.image.name}')
                photo = Photo.objects.get(id=photo.id)
                photo.set_calculated_fields()
                # This is weird, but it makes the image dimensions update on save, just calling .save might not work
                logger.info(logger.info.image, photo.image.width, photo.image.height)
                photo.save()
                logger.info(f'Updated image file for {photo.id} ({photo.external_id})')
            except Exception as e:
                logger.info(e)
                logger.exception(e)
                exception = ApplicationException(exception=traceback.format_exc(), photo=photo)
                exception.save()
