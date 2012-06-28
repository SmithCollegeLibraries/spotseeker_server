from django.contrib import admin
from spotseeker_server.models import *


class SpotAdmin(admin.ModelAdmin):
    """ The admin model for a Spot.
    The ETag is excluded because it is generated on Spot save.
    """
    list_display = ("name",
                    "building_name",
                    "floor",
                    "room_number",
                    "capacity",
                    "organization",
                    "manager")
    list_filter = ["spottypes",
                   "building_name",
                   "organization",
                   "manager"]
    exclude = ('etag',)
admin.site.register(Spot, SpotAdmin)


class SpotImageAdmin(admin.ModelAdmin):
    """ The admin model for a SpotImage.
    Content-type, width, height, and ETag are all filled in by the server on
    SpotImage save.
    """
    exclude = ('content_type', 'width', 'height', 'etag',)
    list_filter = ["spot"]
admin.site.register(SpotImage, SpotImageAdmin)


class SpotAvailableHoursAdmin(admin.ModelAdmin):
    """ The admin model for SpotAvailableHours.
    """
    list_filter = ('day', 'spot')
admin.site.register(SpotAvailableHours, SpotAvailableHoursAdmin)


class SpotExtendedInfoAdmin(admin.ModelAdmin):
    """ The admin model for SpotExtendedInfo.
    """
    list_display = ("spot", "key", "value")
    list_editable = ["key", "value"]
    list_filter = ["key", "spot"]
admin.site.register(SpotExtendedInfo, SpotExtendedInfoAdmin)


admin.site.register(SpotType)
admin.site.register(TrustedOAuthClient)
