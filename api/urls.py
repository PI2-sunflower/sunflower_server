from django.urls import path, include, register_converter
from django.conf.urls import url

from . import views
from utils import converters


register_converter(converters.FourDigitYearConverter, "yyyy")
register_converter(converters.TwoDigitYearConverter, "xx")
register_converter(converters.FloarConverter, "float")

urlpatterns = [
    path("commands", views.get_commands, name="get_commands"),
    path("command-history", views.get_command_history, name="get_command_history"),
    path("track-data", views.get_satellite_data, name="get_satellite_data"),
    path("track/<int:satid>", views.track_satellite, name="track_satellite"),
    path("stop-track", views.stop_tracking, name="stop_tracking"),
    path("mqtt-dispatch", views.mqtt_dispatch, name="mqtt_dispatch"),
    path("set-arm-position", views.set_arm_position, name="set_arm_position"),
    path("get-arm-position", views.get_arm_position, name="get_arm_position"),
    path("get-arm-data", views.get_arm_data, name="get_arm_data"),
    path("set-arm-data", views.set_arm_data, name="set_arm_data"),
    path("get-arm-status", views.get_arm_status, name="get_arm_status"),
]

urlpatterns += [
    path(
        "track_eci/<int:norad>/<yyyy:year>/<xx:month>/<xx:day>/<xx:hour>/"
        "<xx:minute>/<xx:second>/<int:count>/<int:step>",
        views.get_stepped_positions,
        name="track_eci",
    ),
    path(
        "track_azimuth_elevation/<int:norad>/<float:observer_lat>/"
        "<float:observer_lon>/<float:observer_alt>/<yyyy:year>/<xx:month>/"
        "<xx:day>/<xx:hour>/<xx:minute>/<xx:second>/<int:count>/<int:step>",
        views.get_stepped_azimuth_elevation,
        name="track_azimuth_elevation",
    ),
    path('track_az_el_offsets/norad=<int:norad>/lat=<float:lat>/'
         'lon=<float:lon>/alt=<float:alt>/north_offset=<float:north_offset>/'
         'az_offset=<float:az_offset>/el_offset=<float:el_offset>/'
         'year=<yyyy:year>/month=<xx:month>/day=<xx:day>/hour=<xx:hour>/'
         'minute=<xx:minute>/second=<xx:second>/count=<int:count>/'
         'step=<int:step>', views.get_az_el_offsets, name='az_el_offsets'),
]
