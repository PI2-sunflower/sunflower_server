from django.urls import path, include, register_converter
from django.conf.urls import url

from utils import converters
from . import views


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitYearConverter, 'xx')
register_converter(converters.FloarConverter, 'float')

urlpatterns = [
    path('plot_azimuth_elevation/<int:norad>/<float:observer_lat>/' \
         '<float:observer_lon>/<float:observer_alt>/<yyyy:year>/<xx:month>/' \
         '<xx:day>/<xx:hour>/<xx:minute>/<xx:second>/<int:count>/<int:step>',
         views.plot_stepped_azimuth_elevation,
         name='plot_azimuth_elevation'),

    path('plot_az_el_offsets/norad=<int:norad>/lat=<float:lat>/'
         'lon=<float:lon>/alt=<float:alt>/north_offset=<float:north_offset>/'
         'az_offset=<float:az_offset>/el_offset=<float:el_offset>/'
         'year=<yyyy:year>/month=<xx:month>/day=<xx:day>/hour=<xx:hour>/'
         'minute=<xx:minute>/second=<xx:second>/count=<int:count>/'
         'step=<int:step>', views.plot_az_el_offsets, name='plot_az_el_offsets'),
]
