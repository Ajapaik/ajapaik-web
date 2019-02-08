# -*- coding: utf-8 -*-
import datetime
from json import loads

import os
import pytz
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from mock import patch

from ajapaik.ajapaik.curator_drivers.common import CuratorSearchForm
from ajapaik.ajapaik.curator_drivers.fotis import FotisDriver
from ajapaik.ajapaik.models import Photo


# TODO: Throw away postgis so we can use a throwaway sqlite DB for testing
class FunctionalTests(TestCase):
    created_rephotos = []

    def tearDown(self):
        # FIXME: Ugly, we need to remove MEDIA directory hard-coding
        for cr in self.created_rephotos:
            os.remove('/home/ajapaik/ajapaik-web/media/' + cr.image_unscaled.name)
            os.remove('/home/ajapaik/ajapaik-web/media/' + cr.image.name)
            cr.delete()

    def test_api_upload_works_correctly(self):
        c = Client()
        register_response = c.post(reverse('api_register'), {'username': 'test', 'password': 'mellon', 'type': 'auto'})
        parsed_register_response = loads(register_response.content)

        self.assertIsNotNone(parsed_register_response['session'], 'Failed to get session from /register before upload')

        test_photo = Photo.objects.filter(pk=1696).first()

        # TODO: Write tests for EXIF tags that may rotate the image
        # https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image

        # Test landscape image scaled down
        with open(os.path.abspath(os.curdir) + '/ajapaik/ajapaik/test_data/doge_landscape.jpg') as fp:
            upload_response = c.post(reverse('api_photo_upload'), {
                '_s': parsed_register_response['session'],
                '_u': parsed_register_response['id'],
                'id': test_photo.pk,
                'date': '30-12-2010',
                'scale': 0.66,
                'yaw': -3.1394556,
                'pitch': 0.005177597,
                'roll': 0.09593348,
                'original': fp,
                'flip': 0
            })

        parsed_upload_response = loads(upload_response.content)

        self.assertIsNotNone(parsed_upload_response['id'], 'Upload response doesn\'t contain new rephoto ID')

        uploaded_rephoto = Photo.objects.filter(pk=parsed_upload_response['id']).first()

        self.created_rephotos.append(uploaded_rephoto)

        # FIXME: God we've messed up with time zones...
        self.assertEqual(uploaded_rephoto.date,
                         datetime.datetime(2010, 12, 30, hour=1, tzinfo=pytz.timezone('UTC')),
                         'Date parsed incorrectly to %s' % uploaded_rephoto.date)

        scaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image))
        unscaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image_unscaled))

        self.assertEqual(scaled_image.size, (528, 298),
                         'Landscape image scaled down incorrectly to %s, %s' % scaled_image.size)
        self.assertEqual(unscaled_image.size, (800, 453), 'Unscaled image not left untouched')

        # Test landscape image scaled up
        with open(os.path.abspath(os.curdir) + '/ajapaik/ajapaik/test_data/doge_landscape.jpg') as fp:
            upload_response = c.post(reverse('api_photo_upload'), {
                '_s': parsed_register_response['session'],
                '_u': parsed_register_response['id'],
                'id': test_photo.pk,
                'date': '30-12-2010',
                'scale': 1.2,
                'yaw': -3.1394556,
                'pitch': 0.005177597,
                'roll': 0.09593348,
                'original': fp,
                'flip': 0
            })

        parsed_upload_response = loads(upload_response.content)

        uploaded_rephoto = Photo.objects.filter(pk=parsed_upload_response['id']).first()

        self.created_rephotos.append(uploaded_rephoto)

        scaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image))
        unscaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image_unscaled))

        self.assertEqual(scaled_image.size, (960, 543),
                         'Landscape image scaled up incorrectly to %s, %s' % scaled_image.size)
        self.assertEqual(unscaled_image.size, (800, 453), 'Unscaled image not left untouched')

        # Test portrait image scaled down
        with open(os.path.abspath(os.curdir) + '/ajapaik/ajapaik/test_data/doge_portrait.jpg') as fp:
            upload_response = c.post(reverse('api_photo_upload'), {
                '_s': parsed_register_response['session'],
                '_u': parsed_register_response['id'],
                'id': test_photo.pk,
                'date': '30-12-2010',
                'scale': 0.5,
                'yaw': -3.1394556,
                'pitch': 0.005177597,
                'roll': 0.09593348,
                'original': fp,
                'flip': 0
            })

        parsed_upload_response = loads(upload_response.content)

        uploaded_rephoto = Photo.objects.filter(pk=parsed_upload_response['id']).first()

        self.created_rephotos.append(uploaded_rephoto)

        scaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image))
        unscaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image_unscaled))

        self.assertEqual(scaled_image.size, (300, 375),
                         'Portrait image scaled down incorrectly to %s, %s' % scaled_image.size)
        self.assertEqual(unscaled_image.size, (600, 750), 'Unscaled image not left untouched')

        # Test portrait image scaled up
        with open(os.path.abspath(os.curdir) + '/ajapaik/ajapaik/test_data/doge_portrait.jpg') as fp:
            upload_response = c.post(reverse('api_photo_upload'), {
                '_s': parsed_register_response['session'],
                '_u': parsed_register_response['id'],
                'id': test_photo.pk,
                'date': '30-12-2010',
                'scale': 1.5,
                'yaw': -3.1394556,
                'pitch': 0.005177597,
                'roll': 0.09593348,
                'original': fp,
                'flip': 0
            })

        parsed_upload_response = loads(upload_response.content)

        uploaded_rephoto = Photo.objects.filter(pk=parsed_upload_response['id']).first()

        self.created_rephotos.append(uploaded_rephoto)

        scaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image))
        unscaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image_unscaled))

        self.assertEqual(scaled_image.size, (900, 1125),
                         'Portrait image scaled up incorrectly to %s, %s' % scaled_image.size)
        self.assertEqual(unscaled_image.size, (600, 750), 'Unscaled image not left untouched')

    def test_api_register_saves_first_and_last_name(self):
        c = Client()
        register_response = c.post(reverse('api_register'), {'username': 'test', 'password': 'mellon', 'type': 'auto',
                                                             'firstname': 'Lauri', 'lastname': 'Elias'})
        parsed_register_response = loads(register_response.content)

        self.assertIsNotNone(parsed_register_response['session'], 'Failed to get session from /register')

        user = User.objects.filter(pk=parsed_register_response['id']).first()

        self.assertEquals(user.first_name, 'Lauri')
        self.assertEquals(user.last_name, 'Elias')

    # FIXME: Can't get tests to run in staging environment
    # @patch('requests.get')
    # def test_fotis_api_calls_work(self, mocked_get):
    #     mocked_get.return_value.ok = True
    #     driver = FotisDriver()
    #     form = CuratorSearchForm()
    #     form.useFotis = True
    #     form.fullSearch = 'Pääsuke'
    #     self.assertTrue(form.is_valid(), True)
    #     result = driver.search(form.cleaned_data)
    #     self.assertEqual(len(result), 20)
