from django.shortcuts import render
from django.http import JsonResponse

from threading import Thread
from time import sleep

from tracker.fetcher import SatelliteProxy, SatellitePosition

space_station = SatellitePosition()
space_station.satid = 25544

proxy = SatelliteProxy()
proxy.set_position(space_station)
proxy.switch_state("track")


def index(request):
    return render(request, 'index.html')


def get_satellite_data(request):
    position = proxy.get_position()

    data = {
        "satid": position.satid,
        "satname": position.satname,
        "satlatitude": position.satlatitude,
        "satlongitude": position.satlongitude,
        "sataltitude": position.sataltitude,
    }

    return JsonResponse(data)
