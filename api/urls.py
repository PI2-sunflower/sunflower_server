from django.urls import path, include
from django.conf.urls import url

from . import views

urlpatterns = [
    path('api/track-data', views.get_satellite_data, name='get_satellite_data'),
    path('api/track/<int:satid>', views.track_satellite, name='track_satellite'),
    path('api/stop-track', views.stop_tracking, name='stop_tracking'),
]
