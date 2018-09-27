from django.shortcuts import render
from django.http import JsonResponse

from threading import Thread
from time import sleep

from tracker.fetcher import SatelliteProxy, SatellitePosition

# space_station = SatellitePosition()
# space_station.satid = 25544

proxy = SatelliteProxy()


def get_position(position: SatellitePosition):
    data = {
        "satid": position.satid,
        "info": position.info,
        "positions": position.positions,
        "positions_validation": position.positions_validation,
        "tle": position.tle,
    }

    return data


def get_satellite_data(request):
    position = proxy.get_position()
    return JsonResponse(get_position(position))


def track_satellite(request, satid):
    current_position = proxy.get_position()

    if current_position.satid != satid:
        proxy.set_position(SatellitePosition(satid=satid))

    if not proxy.is_tracking():
        proxy.switch_state("track")

    return JsonResponse({"tracking": satid})


def stop_tracking(request):
    proxy.switch_state("not_selected")
    return JsonResponse({"tracking": "stoped"})
