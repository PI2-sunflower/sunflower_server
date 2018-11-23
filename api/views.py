import json

from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from satellite.satellite import Satellite
from satellite.tle_getter import get_and_update_tle, \
     get_and_update_tle_from_disk
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
    message = ""

    if command in VALID_COMMANDS:
        command = AnntenaCommand(command, params)
        (success, message) = command.execute()
    else:
        message = "Invalid command"

    return JsonResponse({"dispatch": success, "message": message})


def get_stepped_positions(request, norad, year, month, day, hour, minute,
                          second, count, step):
    tle = get_and_update_tle(norad)
    start = datetime(year=year,
                     month=month,
                     day=day,
                     hour=hour,
                     minute=minute,
                     second=second,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    positions_dates = satellite.propagate_positions_step(start=start,
                      count=count, step=step)
    positions = []
    for xyz, date in positions_dates:
        x, y, z = xyz
        positions.append({
            'x': x,
            'y': y,
            'z': z,
            'date': date,
        })
    response = {
        'norad_id': norad,
        'count': count,
        'step': step,
        'tle': tle,
        'positions': positions,
    }
    return JsonResponse(response)


def get_stepped_azimuth_elevation(request, norad, observer_lat, observer_lon,
                                  observer_alt, year, month, day, hour, minute,
                                  second, count, step):

    tle = get_and_update_tle(norad)
    start = datetime(year=year,
                     month=month,
                     day=day,
                     hour=hour,
                     minute=minute,
                     second=second,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    az_el, dates = satellite.propagate_az_el_step(observer_lat, observer_lon,
                                observer_alt, start, count=count, step=step)

    az_el_dates = []
    for i, azimuth_elevation in enumerate(az_el):
        azimuth, elevation = azimuth_elevation
        az_el_date = {
            'azimuth': azimuth,
            'elevation': elevation,
            'date': dates[i],
        }
        az_el_dates.append(az_el_date)

    response = {
        'norad_id': norad,
        'observer_latitude': observer_lat,
        'observer_longitude': observer_lon,
        'observer_altitude': observer_alt,
        'count': count,
        'step': step,
        'tle': tle,
        'positions': az_el_dates,
    }
    return JsonResponse(response)

def get_stepped_azimuth_elevation_offset(request, norad, observer_lat,
         observer_lon, observer_alt, north_offset, second, day, month, year,
         count, step):

    tle = get_and_update_tle(norad)
    start = datetime(second=second, day=day, month=month, year=year,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    az_el, dates = satellite.propagate_az_el_step(
        observer_lat, observer_lon, observer_alt, north_offset=north_offset,
        start=start, count=count, step=step)

    az, el = list(zip(*az_el))

    response = {
        'norad_id': norad,
        'observer_latitude': observer_lat,
        'observer_longitude': observer_lon,
        'observer_altitude': observer_alt,
        'north_offset': north_offset,
        'count': count,
        'step': step,
        'tle': tle,
        'azimuth': az,
        'elevation': el,
        'dates': dates,
    }
    return JsonResponse(response)

