from django.urls import path, include, register_converter
from django.conf.urls import url

from utils import converters
from . import views


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitYearConverter, 'xx')
register_converter(converters.FloarConverter, 'float')

urlpatterns = [
    path('plot_azimuth_elevation/<int:norad>/<float:observer_lat>/' \
         '<float:observer_lon>/<float:observer_alt>/<xx:second>/<xx:day>/' \
         '<xx:month>/<yyyy:year>/<int:count>/<int:step>',
         views.plot_stepped_azimuth_elevation,
         name='plot_azimuth_elevation'),
]
