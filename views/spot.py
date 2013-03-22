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

from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import *
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import simplejson as json
from django.db import transaction


class SpotView(RESTDispatch):
    """ Performs actions on a Spot at /api/v1/spot/<spot id>.
    GET returns 200 with Spot details.
    POST to /api/v1/spot with valid JSON returns 200 and creates a new Spot.
    PUT returns 200 and updates the Spot information.
    DELETE returns 200 and deletes the Spot.
    """
    @app_auth_required
    def GET(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
            response = HttpResponse(json.dumps(spot.json_data_structure()))
            response["ETag"] = spot.etag
            response["Content-type"] = "application/json"
            return response
        except:
            response = HttpResponse("Spot not found")
            response.status_code = 404
            return response

    @user_auth_required
    def POST(self, request):
        spot = Spot.objects.create()

        error_response = self.build_and_save_from_input(request, spot)
        if error_response:
            return error_response

        response = HttpResponse()
        response.status_code = 201
        response["Location"] = spot.rest_url()
        return response

    @user_auth_required
    def PUT(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        error_response = self.validate_etag(request, spot)
        if error_response:
            return error_response

        error_response = self.build_and_save_from_input(request, spot)
        if error_response:
            return error_response

        return self.GET(request, spot_id)

    @user_auth_required
    def DELETE(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        error_response = self.validate_etag(request, spot)
        if error_response:
            return error_response

        spot.delete()
        response = HttpResponse()
        response.status_code = 200
        return response

    # These are utility methods for the HTTP methods
    def validate_etag(self, request, spot):
        if not "HTTP_IF_MATCH" in request.META:
            if not "If_Match" in request.META:
                response = HttpResponse('{"error":"If-Match header required"}')
                response.status_code = 409
                return response
            else:
                request.META["HTTP_IF_MATCH"] = request.META["If_Match"]

        if request.META["HTTP_IF_MATCH"] != spot.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response

    @transaction.commit_on_success
    def build_and_save_from_input(self, request, spot):
        body = request.read()
        try:
            new_values = json.loads(body)
        except Exception as e:
            response = HttpResponse('{"error":"Unable to parse JSON"}')
            response.status_code = 400
            return response

        form = SpotForm(new_values)
        if not form.is_valid():
            if request.method == 'POST':
                spot.delete()
            response = HttpResponse(json.dumps(form.errors))
            response.status_code = 400
            return response

        existing_info = spot.json_data_structure()
        for key in spot.json_data_structure():
            if spot.json_data_structure().get(key) is None or spot.json_data_structure().get(key) == {} or spot.json_data_structure().get(key) == '' or spot.json_data_structure().get(key) == [] or key == 'last_modified' or key == 'eTag':
                del existing_info[key]
        if existing_info != new_values:
            errors = []
            #Validate the data POST and record errors and don't make the spot
            if "name" in new_values:
                if new_values["name"]:
                    spot.name = new_values["name"]
                else:
                    errors.append("Invalid name")
            else:
                error.append("Name not provided")

            if "capacity" in new_values:
                if new_values["capacity"]:
                    try:
                        spot.capacity = int(new_values["capacity"])
                    except:
                        pass
            elif spot.capacity is not None:
                spot.capacity = None

            if "type" in new_values:
                for value in new_values["type"]:
                    try:
                        value = SpotType.objects.get(name=value)
                        spot.spottypes.add(value)
                    except:
                        pass
            elif spot.spottypes is not None:
                spot.spottypes.remove()

            if "location" in new_values:
                loc_vals = new_values["location"]
                if "latitude" in loc_vals and "longitude" in loc_vals:
                    try:
                        spot.latitude = float(loc_vals["latitude"])
                        spot.longitude = float(loc_vals["longitude"])

                        # The 2 up there are just to throw the exception below.  They need to not actually be floats
                        spot.latitude = loc_vals["latitude"]
                        spot.longitude = loc_vals["longitude"]
                    except:
                        pass
                        errors.append("Invalid latitude and longitude: %s, %s" % (loc_vals["latitude"], loc_vals["longitude"]))
                else:
                    errors.append("Latitude and longitude not provided")

                if "height_from_sea_level" in loc_vals:
                    try:
                        spot.height_from_sea_level = float(loc_vals["height_from_sea_level"])
                    except:
                        pass
                elif spot.height_from_sea_level is not None:
                    spot.height_from_sea_level = None

                if "building_name" in loc_vals:
                    spot.building_name = loc_vals["building_name"]
                elif spot.building_name != '':
                    spot.building_name = ''
                if "floor" in loc_vals:
                    spot.floor = loc_vals["floor"]
                elif spot.floor != '':
                    spot.floor = ''
                if "room_number" in loc_vals:
                    spot.room_number = loc_vals["room_number"]
                elif spot.room_number != '':
                    spot.room_number = ''
                if "description" in loc_vals:
                    spot.description = loc_vals["description"]
                # TO DO: see if there is a better way of doing the following check
                else:
                    try:
                        if spot.description is not None:
                            spot.description = None
                    except:
                        pass
            else:
                errors.append("Location data not provided")

            if "organization" in new_values:
                spot.organization = new_values["organization"]
            elif spot.organization != '':
                spot.organization = ''
            if "manager" in new_values:
                spot.manager = new_values["manager"]
            elif spot.manager != '':
                spot.manager = ''

            if len(errors) == 0:
                spot.save()
            else:
                spot.delete()
                response = HttpResponse('{"error":"' + str(errors) + '"}')
                response.status_code = 400
                return response

            queryset = SpotAvailableHours.objects.filter(spot=spot)
            queryset.delete()

            if "extended_info" in new_values:
                for item in new_values["extended_info"]:
                    try:
                        info_obj = SpotExtendedInfo.objects.get(spot=spot, key=item)
                        info_obj.value = new_values["extended_info"][item]
                        info_obj.save()
                    except:
                        SpotExtendedInfo.objects.create(key=item, value=new_values["extended_info"][item], spot=spot)
                for info in SpotExtendedInfo.objects.filter(spot=spot).values():
                    if info['key'] not in new_values['extended_info']:
                        SpotExtendedInfo.objects.filter(spot=spot, key=info['key']).delete()
            elif "extended_info" not in new_values:
                SpotExtendedInfo.objects.filter(spot=spot).all().delete()

            try:
                available_hours = new_values["available_hours"]
                for day in [["m", "monday"],
                            ["t", "tuesday"],
                            ["w", "wednesday"],
                            ["th", "thursday"],
                            ["f", "friday"],
                            ["sa", "saturday"],
                            ["su", "sunday"]]:
                    if day[1] in available_hours:
                        day_hours = available_hours[day[1]]
                        for window in day_hours:
                            SpotAvailableHours.objects.create(spot=spot, day=day[0], start_time=window[0], end_time=window[1])
            except:
                pass
