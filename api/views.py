import json

from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from satellite.satellite import Satellite
from satellite.tle_getter import get_and_update_tle
from tracker.fetcher import SatelliteProxy, SatellitePosition, TargetParams, \
    Tracker

# get_client, start_connection, connection_topic
from .mqtt_broker import AnntenaCommand

# space_station = SatellitePosition()
# space_station.satid = 25544

proxy = SatelliteProxy()

# start_connection()

VALID_COMMANDS = [
    "go_up", "go_down", "stop_up_down",
    "expand", "retract", "stop_expand_retract",
    "move_axis",
]


def get_position(position: SatellitePosition):
    data = {
        "satid": position.satid,
        "info": position.info,
        "positions": position.positions,
        "positions_validation": position.positions_validation,
        "tle": position.tle,
    }

    return data


def get_commands(request):
    return JsonResponse(VALID_COMMANDS, safe=False)


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

    command = data.get('command')
    params = data.get('params')
    success = False

    if command in VALID_COMMANDS:
        command = AnntenaCommand(command, params)
        success = command.execute()

        #client = get_client()
        #client.publish(topic, f"{code}")
    if success:
        return JsonResponse({"dispatch": True})
    else:
        return JsonResponse({"dispatch": False})


def get_stepped_positions(request, norad, second, day, month, year,
                          count, step):
    tle = get_and_update_tle(norad)
    start = datetime(second=second, day=day, month=month, year=year,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    positions_dates = satellite.propagate_positions_step(start=start, count=count,
                                                         step=step)
    positions, dates = list(zip(*positions_dates))
    x, y, z = list(zip(*positions))

    response = {
        'norad_id': norad,
        'count': count,
        'step': step,
        'tle': tle,
        'x_position': x,
        'y_position': y,
        'z_position': z,
        'dates': dates,
    }
    return JsonResponse(response)


def get_stepped_azimuth_elevation(request, norad, observer_lat, observer_lon,
                                  observer_alt, second, day, month, year,
                                  count, step):
    tle = get_and_update_tle(norad)
    start = datetime(second=second, day=day, month=month, year=year,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    az_el, dates = satellite.propagate_az_el_step(
        observer_lat, observer_lon, observer_alt, start, count, step)
    az, el = list(zip(*az_el))

    response = {
        'norad_id': norad,
        'observer_latitude': observer_lat,
        'observer_longitude': observer_lon,
        'observer_altitude': observer_alt,
        'count': count,
        'step': step,
        'tle': tle,
        'azimuth': az,
        'elevation': el,
        'dates': dates,
    }
    return JsonResponse(response)
