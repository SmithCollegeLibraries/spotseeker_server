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

    sbutler1@illinois.edu: moved from views/spot.py and adapted for
        the search filter framework.
"""
from spotseeker_server.org_filters import SearchFilter
from django.db.models import Q


class Filter(SearchFilter):
    keys = set((
        'extended_info:noise_level',
        ))

    def filter_query(self, query):
        """Filter based on reservable and noise_level."""

        if 'extended_info:noise_level' in self.request.GET:
            included_levels = \
                self.request.GET.getlist("extended_info:noise_level")
            if included_levels:
                self.has_valid_search_param = True

            if 'quiet' in included_levels or 'moderate' in included_levels:
                included_levels.append('variable')

            excludes = set(['silent', 'quiet', 'moderate', 'variable'])
            # excludes = all noise levels - chosen noise levels
            excludes.difference_update(included_levels)

            for exclude in excludes:
                query = query.exclude(
                    spotextendedinfo__key='noise_level',
                    spotextendedinfo__value__iexact=exclude
                )

        return query
