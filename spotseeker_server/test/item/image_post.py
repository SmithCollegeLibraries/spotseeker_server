""" Copyright 2012, 2013 UW Information Technology, University of Washington
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.conf import settings
from django.core import cache
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from mock import patch
from os.path import abspath, dirname
from spotseeker_server import models
from spotseeker_server.models import Item, Spot
import json
import random
import shutil
import tempfile

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class ItemImagePOSTTest(TestCase):
    """ Tests POSTing to /api/v1/item/<item id>/image.
    """

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()

        spot = Spot.objects.create(name="Test spot for retrieval")
        item = Item.objects.create(name="This is to test adding images",
                                   spot=spot)
        item.save()
        self.spot = spot
        self.item = item

        self.url = '/api/v1/item/{0}/image'.format(self.item.pk)
        self.url = self.url

    def test_jpeg(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a jpeg",
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 201)

    def test_gif(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a gif",
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 201)

    def test_png(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_png.png" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a png",
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 201)

    def test_display_index(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a jpeg",
                                   "display_index": 1,
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 201)

                response = c.get(self.spot.rest_url())
                item_dict = json.loads(response.content)
                item_dict = item_dict['items'][0]
                self.assertEquals(item_dict['images'].__len__(),
                                  1,
                                  "Item has only 1 ItemImage")
                self.assertEquals(item_dict['images'][0]['display_index'],
                                  1,
                                  "Image created with a display index of 1 "
                                  "has a display index of 1")

    def test_no_display_index(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a jpeg",
                                   "image": f})
                f.close()
                self.assertEquals(response.status_code, 201)
                f = open("%s/../resources/test_png.png" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a png",
                                   "image": f})
                f.close()
                self.assertEquals(response.status_code, 201)

                response = c.get(self.spot.rest_url())
                item_dict = json.loads(response.content)
                item_dict = item_dict['items'][0]
                self.assertEquals(item_dict['images'].__len__(),
                                  2,
                                  "Item has 2 ItemImages")
                self.assertEquals(item_dict['images'][0]['display_index'],
                                  0,
                                  "First returned item has a display "
                                  "index of 0")
                self.assertEquals(item_dict['images'][0]['description'],
                                  "This is a jpeg",
                                  "First returned item is the jpeg")
                self.assertEquals(item_dict['images'][1]['display_index'],
                                  1,
                                  "Second returned item has a display index "
                                  "of 1")
                self.assertEquals(item_dict['images'][1]['description'],
                                  "This is a png",
                                  "First returned item is the png")

    def test_invalid_image_type(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_bmp.bmp" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description":
                                   "This is a bmp file - invalid format",
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 400)

    def test_invalid_file(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/fake_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description":
                                   "This is really a text file", "image": f})
                f.close()

                self.assertEquals(response.status_code, 400)

    def test_no_file(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                response = c.post(self.url,
                                  {"description":
                                   "This is really a text file"})

                self.assertEquals(response.status_code, 400)

    def test_wrong_field(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post(self.url,
                                  {"description": "This is a gif",
                                   "not_image": f})
                f.close()

                self.assertEquals(response.status_code, 400)

    def test_wrong_url(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post('/api/v1/item/{0}/image'.
                                  format(self.item.pk + 1),
                                  {"description": "This is a gif",
                                   "image": f})
                f.close()

                self.assertEquals(response.status_code, 404)

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
