from django.urls import path, include, register_converter
from django.conf.urls import url

from . import converters, views


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitYearConverter, 'xx')

urlpatterns = [
    path('api/track-data', views.get_satellite_data, name='get_satellite_data'),
    path('api/track/<int:satid>', views.track_satellite, name='track_satellite'),
    path('api/stop-track', views.stop_tracking, name='stop_tracking'),
    path('api/mqtt-dispatch', views.mqtt_dispatch, name='mqtt_dispatch'),
]

urlpatterns += [
    path('api/positions-interval/<int:satid>/<xx:second>/<xx:day>/<xx:month>' \
         '/<yyyy:year>/<int:count>/<int:step>', views.get_interval_positions,
         name='positions_interval'),
]
