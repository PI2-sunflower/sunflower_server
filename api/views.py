import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from tracker.fetcher import SatelliteProxy, SatellitePosition

from .mqtt_broker import get_client, start_connection, connection_topic

# space_station = SatellitePosition()
# space_station.satid = 25544

proxy = SatelliteProxy()

start_connection()


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


@csrf_exempt
def mqtt_dispatch(request):
    data = json.loads(request.body)

    print("="*80)
    print(data, data.get('code'))
    print("="*80)

    code = data.get('code')
    topic = data.get('topic')

    if code and topic:
        client = get_client()
        client.publish(topic, f"{code}")

        return JsonResponse({"dispatch": True})
    else:
        return JsonResponse({"dispatch": False})
