import json
import math

from datetime import datetime, timedelta, timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from satellite.satellite import Satellite
from satellite.satellite_wrapper import SatelliteWrapper
from satellite.tle_getter import get_and_update_tle
from tracker.fetcher import SatelliteProxy, SatellitePosition, TargetParams, Tracker

# get_client, start_connection, connection_topic
from .mqtt_broker import AnntenaCommand, CommandHistory
from .broker_connection import MQTTConnection

from tracker.position import serialize_arm_position, arm_position_instance
from tracker.data import serialize_arm_data, arm_data_instance

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
    "reset_axis",
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

    position = arm_position_instance()
    updated = False

    try:
        if latitude is not None:
            position.latitude = float(latitude)
        if longitude is not None:
            position.longitude = float(longitude)
        if altitude is not None:
            position.altitude = float(altitude)

        position.save()
        updated = True
    except Exception as e:
        print("position save FAIL")
        print(e)
        updated = False

    return JsonResponse({"updated": updated})


def get_arm_position(request):
    position = arm_position_instance()

    return JsonResponse(serialize_arm_position(position))


def get_arm_data(request):
    arm_data = arm_data_instance()

    return JsonResponse(serialize_arm_data(arm_data))


@csrf_exempt
def set_arm_data(request):
    data = json.loads(request.body)

    operation = data.get("operation")
    angles = data.get("angles")
    magnetometer = data.get("magnetometer")
    engine_speed = data.get("engine_speed")

    arm_data = arm_data_instance()
    updated = False

    try:
        if operation is not None:
            arm_data.operation = operation

        if angles is not None:
            arm_data.error_angle_1 = float(angles.get("angle_1"))
            arm_data.error_angle_2 = float(angles.get("angle_2"))
            arm_data.error_angle_3 = float(angles.get("angle_3"))

        if magnetometer is not None:
            arm_data.magnetometer = float(magnetometer)

        if engine_speed is not None:
            arm_data.engine_speed = math.floor(abs(int(engine_speed)))

        arm_data.save()
        updated = True
    except Exception as e:
        print(e)
        updated = False

    return JsonResponse({"updated": updated})

def get_arm_status(request):
    con = MQTTConnection()

    return JsonResponse({"status": con.status})

def get_az_el_offsets(request, norad, lat, lon, alt, north_offset, az_offset,
                      el_offset, year, month, day, hour, minute, second, count,
                      step):

    start = datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=timezone.utc,
    )


    tle = get_and_update_tle(norad)

    satellite = SatelliteWrapper(*tle)
    az_el, dates = satellite.propagate_az_el_step(lat, lon, alt, start, count,
            step, north_offset=north_offset, azimuth_offset=az_offset,
            elevation_offset=el_offset
    )

    az_el_dates = []
    for i, azimuth_elevation in enumerate(az_el):
        azimuth, elevation = azimuth_elevation
        az_el_date = {"azimuth": azimuth, "elevation": elevation, "date": dates[i]}
        az_el_dates.append(az_el_date)

    response = {
        'norad': norad,
        'observer_latitude': lat,
        'observer_longitude': lon,
        'observer_altitude': alt,
        'north_offset': north_offset,
        'az_offset': az_offset,
        'el_offset': el_offset,
        'start_date': start,
        'count': count,
        'step': step,
        'positions': az_el_dates,
    }
    return JsonResponse(response)
