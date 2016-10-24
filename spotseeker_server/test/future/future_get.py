""" Copyright 2016 UW Information Technology, University of Washington
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
from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo, SpotAvailableHours
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from datetime import datetime, timedelta
from django.utils import timezone


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
class FutureGETTest(TestCase):

    def setUp(self):
        now = timezone.now()
        last_week = now - timedelta(days=7)
        yesterday = now - timedelta(days=1)

        next_week = now + timedelta(days=7)
        tomorrow = now + timedelta(days=1)

        self.now = now
        self.last_week = last_week
        self.yesterday = yesterday
        self.next_week = next_week
        self.tomorrow = tomorrow

        spot1 = Spot.objects.create(name="Testing spot with only past",
                                    latitude=23,
                                    longitude=45)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="true",
            valid_on=last_week,
            valid_until=yesterday,
            spot=spot1)

        self.spot1 = spot1

        spot2 = Spot.objects.create(name="Testing spot with past + current",
                                    latitude=23,
                                    longitude=45)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="true",
            valid_on=last_week,
            valid_until=yesterday,
            spot=spot2)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="no",
            spot=spot2)

        self.spot2 = spot2

        spot3 = Spot.objects.create(name="Testing spot with future",
                                    latitude=23,
                                    longitude=45)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="true",
            valid_on=tomorrow,
            valid_until=next_week,
            spot=spot3)

        self.spot3 = spot3

        spot4 = Spot.objects.create(name="Testing spot with future + current",
                                    latitude=23,
                                    longitude=45)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="true",
            valid_on=tomorrow,
            valid_until=next_week,
            spot=spot4)

        SpotExtendedInfo.objects.create(
            key="has_whiteboards",
            value="no",
            spot=spot4)

        self.spot4 = spot4

        spot5 = Spot.objects.create(name="Testing spot with variations",
                                    latitude=23,
                                    longitude=45)

        SpotExtendedInfo.objects.create(
            key="x_f",
            value="ok2",
            valid_until=tomorrow,
            spot=spot5)

        SpotExtendedInfo.objects.create(
            key="p_x",
            value="ok4",
            valid_on=yesterday,
            spot=spot5)

        SpotExtendedInfo.objects.create(
            key="p_f",
            value="ok3",
            valid_on=yesterday,
            valid_until=tomorrow,
            spot=spot5)

        SpotExtendedInfo.objects.create(
            key="x_x",
            value="ok1",
            spot=spot5)

        self.spot5 = spot5

        spot6 = Spot.objects.create(name="Testing spot for AH",
                                    latitude=23,
                                    longitude=45)

        SpotAvailableHours.objects.create(spot=spot6,
                                          day="m",
                                          start_time="11:00",
                                          end_time="14:00")
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="m",
                                          start_time="00:00",
                                          end_time="10:00",
                                          valid_on=yesterday,
                                          valid_until=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="t",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=yesterday,
                                          valid_until=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="w",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=yesterday)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="th",
                                          start_time="11:00",
                                          end_time="14:00")
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="f",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=yesterday,
                                          valid_until=next_week)

        SpotAvailableHours.objects.create(spot=spot6,
                                          day="m",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="m",
                                          start_time="00:00",
                                          end_time="10:00",
                                          valid_on=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="t",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="w",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="th",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=next_week)
        SpotAvailableHours.objects.create(spot=spot6,
                                          day="f",
                                          start_time="11:00",
                                          end_time="14:00",
                                          valid_on=next_week)

        self.spot6 = spot6

    def compare_available_hours_json(self, hours_json, hours):
        """Compares the avaiable hours JSON returned from the server
        to the model."""

        day_hours = hours_json[hours.get_day_display()]

        for hour in day_hours:
            if hour == hours.json_data_structure():
                return True

        return False

    def compare_available_hours_full_json(self, full_hours_json, hours):
        """Compares the full avaiable hours JSON returned from the server
        to the model."""

        for hour in full_hours_json:
            if hour == hours.full_json_data_structure():
                return True

        return False

    def test_spot_past_extended_info(self):
        url = "/api/v1/spot/%s" % self.spot1.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_spot, self.spot1)

        self.assertEquals(spot_dict['future_extended_info'], [])
        self.assertEquals(spot_dict['extended_info'], {})

    def test_spot_past_plus_current(self):
        url = "/api/v1/spot/%s" % self.spot2.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_spot, self.spot2)

        self.assertEquals(spot_dict['future_extended_info'], [])
        self.assertEquals(spot_dict['extended_info']['has_whiteboards'], 'no')

    def test_spot_future_extended_info(self):
        url = "/api/v1/spot/%s" % self.spot3.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_spot, self.spot3)

        self.assertEquals(len(spot_dict['future_extended_info']), 1)
        whiteboards = spot_dict['future_extended_info'][0]['has_whiteboards']
        self.assertEquals(whiteboards, 'true')
        self.assertEquals(spot_dict['future_extended_info'][0]['valid_on'],
                          self.tomorrow.isoformat())
        self.assertEquals(spot_dict['future_extended_info'][0]['valid_until'],
                          self.next_week.isoformat())
        self.assertEquals(spot_dict['extended_info'], {})

    def test_spot_future_plus_current_extended_info(self):
        url = "/api/v1/spot/%s" % self.spot4.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_spot, self.spot4)

        self.assertEquals(len(spot_dict['future_extended_info']), 1)
        whiteboards = spot_dict['future_extended_info'][0]['has_whiteboards']
        self.assertEquals(whiteboards, 'true')
        self.assertEquals(spot_dict['future_extended_info'][0]['valid_on'],
                          self.tomorrow.isoformat())
        self.assertEquals(spot_dict['future_extended_info'][0]['valid_until'],
                          self.next_week.isoformat())
        self.assertEquals(spot_dict['extended_info']['has_whiteboards'], 'no')

    def test_spot_multiple_ways_of_now(self):
        url = "/api/v1/spot/%s" % self.spot5.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_spot, self.spot5)

        self.assertEquals(spot_dict['extended_info']['x_x'], 'ok1')
        self.assertEquals(spot_dict['extended_info']['x_f'], 'ok2')
        self.assertEquals(spot_dict['extended_info']['p_f'], 'ok3')
        self.assertEquals(spot_dict['extended_info']['p_x'], 'ok4')

        self.assertEquals(len(spot_dict['future_extended_info']), 2)

    def test_available_hours(self):
        url = "/api/v1/spot/%s" % self.spot6.pk
        response = self.client.get(url)
        spot_dict = json.loads(response.content)

        current_hours = self.spot6.get_current(SpotAvailableHours)
        full_hours = SpotAvailableHours.objects.filter(spot=self.spot6)

        current_hours_json = spot_dict['available_hours']
        full_hours_json = spot_dict['full_available_hours']

        # ensure that we are getting the correct data
        for hours in current_hours:
            match = self.compare_available_hours_json(current_hours_json,
                                                      hours)
            self.assertTrue(match)

        for hours in full_hours:
            match = self.compare_available_hours_full_json(full_hours_json,
                                                           hours)
            self.assertTrue(match)

    def tearDown(self):
        self.spot1.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()
        self.spot5.delete()
        self.spot6.delete()
