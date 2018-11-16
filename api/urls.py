from django.urls import path, include, register_converter
from django.conf.urls import url

from . import views
from utils import converters


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitYearConverter, 'xx')
register_converter(converters.FloarConverter, 'float')

urlpatterns = [
    path('commands', views.get_commands, name="get_commands"),
    path('track-data', views.get_satellite_data, name='get_satellite_data'),
    path('track/<int:satid>', views.track_satellite, name='track_satellite'),
    path('stop-track', views.stop_tracking, name='stop_tracking'),
    path('mqtt-dispatch', views.mqtt_dispatch, name='mqtt_dispatch'),
]

urlpatterns += [
    path('track_eci/<int:norad>/<yyyy:year>/<xx:month>/<xx:day>/<xx:hour>/' \
         '<xx:minute>/<xx:second>/<int:count>/<int:step>',
         views.get_stepped_positions, name='track_eci'),

    path('track_azimuth_elevation/<int:norad>/<float:observer_lat>/' \
         '<float:observer_lon>/<float:observer_alt>/<yyyy:year>/<xx:month>/' \
         '<xx:day>/<xx:hour>/<xx:minute>/<xx:second>/<int:count>/<int:step>',
         views.get_stepped_azimuth_elevation,
         name='track_azimuth_elevation'),
#def propagate(self, year, month=1, day=1, hour=0, minute=0, second=0.0):
]
