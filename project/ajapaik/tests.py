# -*- coding: utf-8 -*-
from json import loads

import os
from PIL import Image
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from project.ajapaik.models import Photo

from django.conf import settings


class FunctionalTests(TestCase):
    def test_api_uploaded_image_is_scaled_correctly(self):
        c = Client()
        register_response = c.post(reverse('api_register'), {'username': 'test', 'password': 'mellon', 'type': 'auto'})
        parsed_register_response = loads(register_response.content)

        self.assertIsNotNone(parsed_register_response['session'], 'Failed to get session from /register before upload')

        test_photo = Photo.objects.filter(pk=1696).first()

        with open(os.path.abspath(os.curdir) + '/project/ajapaik/test_data/doge.jpeg') as fp:
            upload_response = c.post(reverse('api_photo_upload'), {
                '_s': parsed_register_response['session'],
                '_u': parsed_register_response['id'],
                'id': test_photo.pk,
                'date': '2017-09-06 22:27',
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
        scaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image))
        unscaled_image = Image.open(settings.MEDIA_ROOT + '/' + str(uploaded_rephoto.image_unscaled))

        self.assertEqual(scaled_image.size, (264, 264))
        self.assertEqual(unscaled_image.size, (400, 400))

        uploaded_rephoto.image_unscaled.delete()
        uploaded_rephoto.image.delete()
        uploaded_rephoto.delete()
