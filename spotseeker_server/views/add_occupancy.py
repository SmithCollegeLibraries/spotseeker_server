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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to a simplier RESTDispatch framework.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException
from spotseeker_server.models import Occupancy, Spot
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import json

class AddOccupancyView(RESTDispatch):
    """ Saves an Occupancy for a particular Spot on POST to
        /api/v1/spot/<spot id>/occupancy.
    """
    @user_auth_required
    @admin_auth_required
    def POST(self, request, spot_id):

        spot = Spot.objects.get(pk=spot_id)
        data = json.loads(request.body)

        args = {
            'upload_application': request.META.get('SS_OAUTH_CONSUMER_NAME', ''),
            'upload_user': request.META.get('SS_OAUTH_USER', ''),
            'students': int(data['students']),
            'minutes': int(data['minutes'])
        }

        if args['students'] != None and args['minutes'] != None:
            occupancy = spot.occupancy_set.create(**args)
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=404)
