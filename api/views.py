import json

from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from satellite.satellite import Satellite
from satellite.tle_getter import get_and_update_tle
from tracker.fetcher import SatelliteProxy, SatellitePosition, TargetParams, Tracker

# get_client, start_connection, connection_topic
from .mqtt_broker import AnntenaCommand, CommandHistory

from tracker.position import serialize_arm_position, arm_position_instance

# space_station = SatellitePosition()
# space_station.satid = 25544

proxy = SatelliteProxy()

# start_connection()

VALID_COMMANDS = [
    "go_up",
    "go_down",
    "stop_up_down",
    "expand",
    "retract",
    "stop_expand_retract",
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

def get_command_history(request):
    history = CommandHistory().history

    return JsonResponse(history, safe=False)


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

    command = data.get("command")
    params = data.get("params")
    success = False
    message = ""

    if command in VALID_COMMANDS:
        command = AnntenaCommand(command, params)
        (success, message) = command.execute()
    else:
        message = "Invalid command"

    return JsonResponse({"dispatch": success, "message": message})


def get_stepped_positions(
    request, norad, year, month, day, hour, minute, second, count, step
):
    tle = get_and_update_tle(norad)
    start = datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=timezone.utc,
    )

    satellite = Satellite(*tle)
    positions_dates = satellite.propagate_positions_step(
        start=start, count=count, step=step
    )
    positions = []
    for xyz, date in positions_dates:
        x, y, z = xyz
        positions.append({"x": x, "y": y, "z": z, "date": date})
    response = {
        "norad_id": norad,
        "count": count,
        "step": step,
        "tle": tle,
        "positions": positions,
    }
    return JsonResponse(response)


def get_stepped_azimuth_elevation(
    request,
    norad,
    observer_lat,
    observer_lon,
    observer_alt,
    year,
    month,
    day,
    hour,
    minute,
    second,
    count,
    step,
):

    tle = get_and_update_tle(norad)
    start = datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=timezone.utc,
    )

    satellite = Satellite(*tle)
    az_el, dates = satellite.propagate_az_el_step(
        observer_lat, observer_lon, observer_alt, start, count, step
    )

    az_el_dates = []
    for i, azimuth_elevation in enumerate(az_el):
        azimuth, elevation = azimuth_elevation
        az_el_date = {"azimuth": azimuth, "elevation": elevation, "date": dates[i]}
        az_el_dates.append(az_el_date)

    response = {
        "norad_id": norad,
        "observer_latitude": observer_lat,
        "observer_longitude": observer_lon,
        "observer_altitude": observer_alt,
        "count": count,
        "step": step,
        "tle": tle,
        "positions": az_el_dates,
    }
    return JsonResponse(response)


@csrf_exempt
def set_arm_position(request):
    data = json.loads(request.body)

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    altitude = data.get("altitude")
    magnetometer = data.get("magnetometer")
    engine_speed = data.get("engine_speed")

    position = arm_position_instance()

    if latitude is not None:
        position.latitude = latitude
    if longitude is not None:
        position.longitude = longitude
    if altitude is not None:
        position.altitude = altitude
    if magnetometer is not None:
        position.magnetometer = magnetometer
    if engine_speed is not None:
        position.engine_speed = engine_speed

    position.save()

    return JsonResponse({"updates": "done"})


def get_arm_position(request):
    position = arm_position_instance()

    return JsonResponse(serialize_arm_position(position))
