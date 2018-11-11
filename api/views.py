import json

from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from satellite.satellite import Satellite
from tracker.fetcher import SatelliteProxy, SatellitePosition, TargetParams, \
    Tracker

# get_client, start_connection, connection_topic
from .mqtt_broker import AnntenaCommand

# space_station = SatellitePosition()
# space_station.satid = 25544

proxy = SatelliteProxy()

# start_connection()


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
    success = False

    if code and topic:
        command = AnntenaCommand(code, topic)
        success = command.execute()

        #client = get_client()
        #client.publish(topic, f"{code}")
    if success:
        return JsonResponse({"dispatch": True})
    else:
        return JsonResponse({"dispatch": False})

def get_interval_positions(request, satid, second, day, month, year,
                           count, step):
    tracker = Tracker(satid=satid)
    tle = tracker.fetch(target=TargetParams.TLE).get('tle', None)
    tle = tle.split('\r\n')

    start = datetime(second=second, day=day, month=month, year=year,
            tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    positions_dates = satellite.propagate_positions_step(start=start, count=count,
                   step=step)
    positions, dates = list(zip(*positions_dates))
    x, y, z = list(zip(*positions))

    response = {
        'satid': satid,
        'start': start,
        'count': count,
        'step': step,
        'tle': tle,
        'x_position': x,
        'y_position': y,
        'z_position': z,
        'dates': dates,
    }
    return JsonResponse(response)
