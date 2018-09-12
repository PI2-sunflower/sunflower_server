from django.urls import path, include
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('get-satellite-data', views.get_satellite_data, name='get_satellite_data'),
]
