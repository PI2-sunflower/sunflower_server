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
    def __init__(self, satid: int):
        self.API_URI = self._build_uri(satid)

    def fetch_position(self):
        with request.urlopen(self.API_URI) as response:
            data = json.loads(response.read())
            return data

    def _build_uri(self, satid: int) -> str:
        uri = f"{BASE_URI}/satellite/positions/{satid}/{MY_LAT}/{MY_LONG}/{MY_ALT}/1/&apiKey={API_KEY}"
        return uri


class SatellitePosition:
    __slots__ = ('satid', 'satname', 'satlatitude',
                 'satlongitude', 'sataltitude',)

    def __init__(self,
                 satid=None,
                 satname=None,
                 satlatitude=None,
                 satlongitude=None,
                 sataltitude=None):

        self.satid = satid
        self.satname = satname
        self.satlatitude = satlatitude
        self.satlongitude = satlongitude
        self.sataltitude = sataltitude


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

                    info = data.get('info')
                    positions = data.get('positions')

                    self.position.satid = info['satid']
                    self.position.satname = info['satname']
                    self.position.satlatitude = positions[0]['satlatitude']
                    self.position.satlongitude = positions[0]['satlongitude']
                    self.position.sataltitude = positions[0]['sataltitude']
                except:
                    print("Could not get satellite data")
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
