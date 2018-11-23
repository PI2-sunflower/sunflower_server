import pickle
from datetime import datetime, timezone

from django.utils import timezone

from api.models import Tle
from tracker.fetcher import TargetParams, Tracker
from satellite.tle import TLE

TLE_UPDATE_TIME = 30 # Unit: seconds


def fetch_new_tle(norad):
    tracker = Tracker(satid=norad)
    tle = tracker.fetch(target=TargetParams.TLE).get('tle', None)
    tle = tle.split('\r\n')
    tle_wrapper = TLE(*tle)
    return tle_wrapper

def get_and_update_tle_from_disk(norad_id):
    assert(isinstance(norad_id, int))

    TLE_CACHE_FILEPATH = 'tle_cache.pickle'
    DOWNLOADED_AT_KEY = 'downloaded_at'
    READ_MODE = 'rb'
    WRITE_MODE = 'wb'
    LINE1, LINE2 = 'line1', 'line2'

    now = datetime.now(tz=timezone.utc)
    should_download_tle = True

    tle_value = None

    try:
        tle_cache_file = open(TLE_CACHE_FILEPATH, READ_MODE)
        tle_cache = pickle.load(tle_cache_file)
        if norad_id in tle_cache:
            tle_value = tle_cache[norad_id]
            time_delta = now - tle_value[DOWNLOADED_AT_KEY]
            if time_delta.total_seconds() < TLE_UPDATE_TIME:
                should_download_tle = False
    except FileNotFoundError:
        tle_cache = {}

    if should_download_tle:
        print('Downloading new TLE for NORAD={}'.format(norad_id))
        tle = fetch_new_tle(norad=norad_id)

        tle_value = {
            DOWNLOADED_AT_KEY: now,
            LINE1: tle.tle_line1,
            LINE2: tle.tle_line2,
        }

        tle_cache[norad_id] = tle_value
        tle_cache_file = open(TLE_CACHE_FILEPATH, WRITE_MODE)
        pickle.dump(tle_cache, tle_cache_file)

    return tle_value[LINE1], tle_value[LINE2]


def save_or_update_tle_in_db(tle):
    assert(len(tle) == 2)

def get_and_update_tle(norad):
    should_fetch_tle = False
    now = timezone.now()
    try:
        tle = Tle.objects.get(norad=norad)
        update_delta = now - tle.updated_at
        if update_delta.total_seconds() < TLE_UPDATE_TIME:
            response = tle.line1, tle.line2
        else:
            print('Current TLE for NORAD={} is outdated.'.format(norad))
            should_fetch_tle = True
    except Tle.DoesNotExist:
        print('No TLE for NORAD={} on database.'.format(norad))
        should_fetch_tle = True

    if should_fetch_tle:
        print('Downloading and updating database TLE for norad=[{}]'.format(norad))
        tle = fetch_new_tle(norad)
        new_tle_value = {
            'line1': tle.tle_line1,
            'line2': tle.tle_line2,
            'updated_at': now,
        }
        Tle.objects.update_or_create(norad=norad, defaults=new_tle_value)
        response = tle.tle

    return response

if __name__ == '__main__':
    norad = 25544
    print('get_and_update_tle_from_disk = {}'.format(get_and_update_tle_from_disk))


