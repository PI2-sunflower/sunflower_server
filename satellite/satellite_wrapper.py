from datetime import timedelta

from satellite.satellite import Satellite


METERS_IN_A_KILOMETER = 1000.0


class SatelliteWrapper:
    '''This is a wrapper of sgp4.model.satellite and pymap3d modules.'''

    def __init__(self, tle_line1, tle_line2):
        self.satellite = Satellite(tle_line1, tle_line2)

    def get_observer_azimuth_elevation(self, observer_latitude,
                                       observer_longitude,
                                       observer_altitude, date,
                                       north_offset=0.0,
                                       azimuth_offset=0.0,
                                       elevation_offset=0.0):

        az, el = self.satellite.get_observer_azimuth_elevation(
            observer_latitude, observer_longitude, observer_altitude, date,
            north_offset=north_offset)

        az = (az + azimuth_offset) % 360.0
        el = el + elevation_offset
        if el > 90.0:
            el = 180.0 - el
            az = (az + 180.0) % 360.0

        if az < 0.0 or az > 360.0:
            raise ValueError('Offsets produced an azimuth of {} wich is'
                             ' outside of the range [0, 360]'.format(az))
        if el < -90.0 or el > 90.0:
            raise ValueError('Offsets produced an elevation of {} wich is'
                             ' outside of the range [-90, +90]'.format(el))
        return az, el

    def propagate_az_el_step(self, observer_lat, observer_lon, observer_alt,
                             start, count, step, north_offset=0.0,
                             azimuth_offset=0.0, elevation_offset=0.0):
        dates = [start + timedelta(seconds=step * i) for i in range(count)]
        az_el = [self.get_observer_azimuth_elevation(observer_lat,
                 observer_lon, observer_alt, date,
                 north_offset=north_offset, azimuth_offset=azimuth_offset,
                 elevation_offset=elevation_offset) for date in dates]
        return az_el, dates
