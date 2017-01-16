# -*- coding: utf-8 -*-
""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License


    This provides a management command to django's manage.py called
    create_sample_spots that will generate a set of spots for testing.
"""
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from spotseeker_server.models import *
from django.core.files import File
from decimal import *
import os
import csv
import string

class Command(BaseCommand):
    help = 'Import spots from csv'

    option_list = BaseCommand.option_list + (
        make_option(
            '--replace',
            dest='replace',
            default=False,
            help='Delete all existing spots prior to import',),
        make_option(
            '--imgdir',
            dest='imgdir',
            default='spot_images',
            help='Folder from which to import spot images.',),
    )

    def handle(self, *args, **options):

        if options['replace']:
            Spot.objects.all().delete()
            SpotExtendedInfo.objects.all().delete()
            SpotAvailableHours.objects.all().delete()

        with open(args[0]) as csv_file:

          csv_reader = csv.reader(csv_file)
          next(csv_file) # skip header

          for row in csv_reader:
            (_, _, _, _, name, location_description, room_number, floor, orientation,
              manager, editors, modified_by, owner, building_name, spottype, latitude, longitude, capacity,
              has_whiteboards, has_outlets, has_printing, has_scanner, has_displays, has_projector,
              num_computers, has_computers, has_natural_light, noise_level, food_nearby,
              available_hours, hours_notes, cafe_hours, display_access_restrictions,
              access_notes, reservable, reservation_notes, campus, has_labstats, labstats_id,
              imagenames, owning_group) = row

            print
            print "Creating", name

            spot = Spot.objects.create(
                name=name,
                longitude=Decimal(longitude),
                latitude=Decimal(latitude),
                building_name=building_name,
                floor=floor,
                room_number=room_number,
                capacity=capacity,
                display_access_restrictions=display_access_restrictions,
                manager=manager
                )

            spottype = SpotType.objects.get_or_create(name=spottype)[0]
            spot.spottypes.add(spottype)

            if campus != "":
                spot.spotextendedinfo_set.create(key="campus", value=campus.lower())
            if location_description != "":
                spot.spotextendedinfo_set.create(key="location_description", value=location_description)
            if has_whiteboards != "":
                spot.spotextendedinfo_set.create(key="has_whiteboards", value=has_whiteboards=="true")
            if has_outlets != "":
                spot.spotextendedinfo_set.create(key="has_outlets", value=has_outlets=="true")
            if has_printing != "":
                spot.spotextendedinfo_set.create(key="has_printing", value=has_printing=="true")
            if has_scanner != "":
                spot.spotextendedinfo_set.create(key="has_scanner", value=has_scanner=="true")
            if has_displays != "":
                spot.spotextendedinfo_set.create(key="has_displays", value=has_displays=="true")
            if has_projector != "":
                spot.spotextendedinfo_set.create(key="has_projector", value=has_projector=="true")
            if num_computers != "":
                spot.spotextendedinfo_set.create(key="num_computers", value=num_computers)
            if has_computers != "":
                spot.spotextendedinfo_set.create(key="has_computers", value=has_computers=="true")
            if has_natural_light != "":
                spot.spotextendedinfo_set.create(key="has_natural_light", value=has_natural_light=="true")
            if noise_level != "":
                spot.spotextendedinfo_set.create(key="noise_level", value=noise_level)
            if food_nearby != "":
                spot.spotextendedinfo_set.create(key="food_nearby", value=food_nearby)
            if access_notes != "":
                spot.spotextendedinfo_set.create(key="access_notes", value=access_notes)
            if reservable != "":
                spot.spotextendedinfo_set.create(key="reservable", value=reservable)
            if reservation_notes != "":
                spot.spotextendedinfo_set.create(key="reservation_notes", value=reservation_notes)

            for imagename in imagenames.split(', '):
                image = open(os.path.join(options['imgdir'], imagename.strip()))
                spot.spotimage_set.create(image=File(image))

            for available_hour in available_hours.strip('"').split(', '):
                (day, hours) = available_hour.split(': ')
                (start_time, end_time) = hours.split('-')
                if day == 'Fr': day = 'F'
                if day == 'S': day = 'Sa'
                spot.spotavailablehours_set.create(
                    day=day.lower(),
                    start_time=start_time,
                    end_time=end_time
                    )

            spot.save()
