import json
import os
from urllib import request



API_KEY = os.environ.get('N2YO_API_KEY', "blank")
BASE_URI = "https://www.n2yo.com/rest/v1"
ID = "25544"
MY_LAT = "-15.77972"
MY_LONG = "-47.92972"
MY_ALT = "0"

SATELLITE_URI = f"{BASE_URI}/satellite/positions/{ID}/{MY_LAT}/{MY_LONG}/{MY_ALT}/1/&apiKey={API_KEY}"


class Satellite:
    __slots__ = 'satid', 'satname', 'satlatitude', 'satlongitude', 'sataltitude'

    def __init__(self):
        self.satid = None
        self.satname = None
        self.satlatitude = None
        self.satlongitude = None
        self.sataltitude = None

    def set_data(self, info, positions):
        self.satid = info['satid']
        self.satname = info['satname']
        self.satlatitude = positions[0]['satlatitude']
        self.satlongitude = positions[0]['satlongitude']
        self.sataltitude = positions[0]['sataltitude']

    def get_data(self):
        data = {
            "satid": self.satid,
            "satname": self.satname,
            "satlatitude": self.satlatitude,
            "satlongitude": self.satlongitude,
            "sataltitude": self.sataltitude,
        }

        return data


satellite_data = Satellite()

del Satellite  # satellite_data will be the only instance of Satellite


def get_satellite(satellite):
    with request.urlopen(SATELLITE_URI) as response:
        data = json.loads(response.read())

        try:
            satellite.set_data(data['info'], data['positions'])
        except:
            print("Could not get satellite data")
