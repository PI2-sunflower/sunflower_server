import json
import os
import abc
from urllib import request

from threading import Thread
from time import sleep


API_KEY = os.environ.get('N2YO_API_KEY', "blank")
BASE_URI = "https://www.n2yo.com/rest/v1"
ID = "25544"
MY_LAT = "-15.77972"
MY_LONG = "-47.92972"
MY_ALT = "0"

SATELLITE_URI = f"{BASE_URI}/satellite/positions/{ID}/{MY_LAT}/{MY_LONG}/{MY_ALT}/1/&apiKey={API_KEY}"


class Tracker:
    __slots__ = ('satid',)

    def __init__(self, satid: int):
        self.satid = satid

    def fetch_position(self):
        request_uri = self._positions_uri

        with request.urlopen(request_uri) as response:
            content = response.read()

            if type(content) == bytes:
                content = content.decode('utf-8')

            data = json.loads(content)

            return data

    @property
    def _positions_uri(self):
        return "{}/satellite/positions/{}/{}/{}/{}/1/&apiKey={}".format(
            BASE_URI, self.satid, MY_LAT, MY_LONG, MY_ALT, API_KEY
        )

    @property
    def __tle_uri(self):
        f"{BASE_URI}/satellite/tle/{self.satid}&apiKey={API_KEY}"


class SatellitePosition:
    __slots__ = ('satid', 'info', 'positions', 'tle',)

    def __init__(self,
                 satid=None,
                 info=None,
                 positions=None,
                 tle=None):

        self.satid = satid
        self.info = info
        self.positions = positions
        self.tle = tle


class Satellite(abc.ABC):
    @abc.abstractmethod
    def set_position(self, position: SatellitePosition):
        pass

    @abc.abstractmethod
    def get_position(self) -> SatellitePosition:
        pass


class SatelliteNotSelectedState(Satellite):
    def set_position(self, position: SatellitePosition):
        pass

    def get_position(self) -> SatellitePosition:
        return SatellitePosition()


class SatelliteFixedState(Satellite):
    def __init__(self, position: SatellitePosition):
        self.position = position

    def set_position(self, position: SatellitePosition):
        self.position = position

    def get_position(self) -> SatellitePosition:
        return self.position


class SatelliteTrackerState(Satellite):
    def __init__(self, position):
        self._keep_tracking = False
        self.set_position(position)

    def set_position(self, position: SatellitePosition):
        self.position = position

    def get_position(self) -> SatellitePosition:
        return self.position

    def stop_tracking(self):
        self._keep_tracking = False

    def start_tracking(self):
        if not self._keep_tracking:
            self._keep_tracking = True
            self._track_position()

    def _track_position(self):
        tracker = Tracker(self.position.satid)

        def track_thread():
            while self._keep_tracking:
                print("Fetching satellite data")
                try:
                    data = tracker.fetch_position()

                    info = data.get('info', None)
                    positions = data.get('positions', None)

                    if info is not None:
                        self.position.info = info

                    if positions is not None:
                        self.position.positions = positions

                except Exception as e:
                    print(f"Could not get satellite data: {e}")
                    self.position = SatellitePosition()

                sleep(3)

        t = Thread(target=track_thread)
        t.start()


class SatelliteProxy(Satellite):
    def __init__(self):
        self.satellite = SatelliteNotSelectedState()
        self.position = self.satellite.get_position()

    def set_position(self, position: SatellitePosition):
        self.position = position

    def get_position(self) -> SatellitePosition:
        return self.satellite.get_position()

    def is_tracking(self) -> bool:
        return isinstance(self.satellite, SatelliteTrackerState)

    def switch_state(self, next_state: str):
        tracking = self.is_tracking()

        if tracking:
            self.satellite.stop_tracking()  # stop thread

        if next_state == "fixed":
            self.satellite = SatelliteFixedState(self.position)
        elif next_state == "track":
            if tracking:
                self.satellite.set_position(self.position)
            else:
                self.satellite = SatelliteTrackerState(self.position)
                self.satellite.start_tracking()
        else:  # anything else goto not selected state
            self.satellite = SatelliteNotSelectedState()
