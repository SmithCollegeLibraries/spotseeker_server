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

    sbutler1@illinois.edu: adapted to the new form framework.
"""

from django import forms
from django.dispatch import receiver
from spotseeker_server.default_forms.spot import DefaultSpotForm
from spotseeker_server.default_forms.spot import DefaultSpotExtendedInfoForm
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.dispatch import spot_post_build
import simplejson as json


# dict of all of the smith extended info with values that must be validated
# and what all of the possible validated values are, or validated types
validated_ei = {
    "campus": ['smith'],
    "has_computers": ['true'],
    "has_displays": ['true'],
    "has_natural_light": ['true'],
    "has_outlets": ['true'],
    "has_printing": ['true'],
    "has_projector": ['true'],
    "has_scanner": ['true'],
    "has_whiteboards": ['true'],
    "is_hidden": ['true'],
    "noise_level": ['silent', 'quiet', 'moderate', 'variable'],
    "num_computers": "int",
    "rating": "int",
    "review_count": "int"
}


def smith_validate(value, key, choices):
    """ Check to see if the value is one of the choices or if it is an int,
        else it throws a validation error
    """
    if choices == "int":
        try:
            int(value)
        except:
            raise forms.ValidationError("Value must be an int")
    elif value not in choices:
        raise forms.ValidationError(
            'Value for %s was %s, must be one of: %s'
            % (key, repr(value), '; '.join((repr(c) for c in choices))))


class SmithSpotExtendedInfoForm(DefaultSpotExtendedInfoForm):

    def clean(self):
        cleaned_data = super(SmithSpotExtendedInfoForm, self).clean()

        # Have to check value here since we look at multiple items
        key = self.cleaned_data['key']
        value = self.cleaned_data['value']

        if key in validated_ei:
            smith_validate(value, key, validated_ei[key])

        return cleaned_data


class SmithSpotForm(DefaultSpotForm):
    validated_extended_info = validated_ei


@receiver(spot_post_build, sender=SmithSpotForm)
def smith_validate_has_extended_info(sender, **kwargs):
    """
    After a spot REST request has been processed, validate that it contained
    some extended info.
    """
    spot = kwargs['spot']
    if spot.spotextendedinfo_set.count() <= 0:
        raise forms.ValidationError("SmithSpot must have extended info")
