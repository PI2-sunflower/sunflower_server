import json

from datetime import datetime, timedelta, timezone
from django.http import JsonResponse
from satellite.satellite_wrapper import SatelliteWrapper
from satellite.tle_getter import get_and_update_tle

from django.http import HttpResponse

from plotter import plotter
from satellite.satellite import Satellite
from satellite.tle_getter import get_and_update_tle_from_disk
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt

import io


def plot_stepped_azimuth_elevation(request, norad, observer_lat, observer_lon,
                                   observer_alt, year, month, day, hour,
                                   minute, second, count, step):
    tle = get_and_update_tle_from_disk(norad)
    start = datetime(year=year,
                     month=month,
                     day=day,
                     hour=hour,
                     minute=minute,
                     second=second,
                     tzinfo=timezone.utc)

    satellite = Satellite(*tle)
    az_el, dates = satellite.propagate_az_el_step(observer_lat, observer_lon,
    observer_alt, start=start, count=count, step=step)
    az, el = list(zip(*az_el))

    figure = plotter.plot_az_el(az, el)
    TITLE_FONT_SIZE = 10
    plt.title('NORAD: {}'.format(norad), fontsize=TITLE_FONT_SIZE)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(figure)
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response

def plot_az_el_offsets(request, norad, lat, lon, alt, north_offset, az_offset,
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

    az, el = list(zip(*az_el))

    figure = plotter.plot_az_el(az, el)
    TITLE_FONT_SIZE = 10
    plt.title('NORAD: {}'.format(norad), fontsize=TITLE_FONT_SIZE)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(figure)
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response

