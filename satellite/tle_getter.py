import pickle
from datetime import datetime, timezone

from django.utils import timezone

from tracker.fetcher import TargetParams, Tracker
from satellite.tle import TLE

from urllib.request import urlopen

TLE_UPDATE_TIME = 60 * 60 # Unit: seconds

TLE_CACHE_FILEPATH = 'tle_cache.pickle'
DOWNLOADED_AT_KEY = 'downloaded_at'

def fetch_new_tle(norad):
    tracker = Tracker(satid=norad)
    tle = tracker.fetch(target=TargetParams.TLE).get('tle', None)
    if not tle:
        raise ValueError('Invalid NORAD')

    tle = tle.split('\r\n')
    tle_wrapper = TLE(*tle)
    return tle_wrapper

def get_tle_cache_from_disk():
    READ_MODE = 'rb'
    with open(TLE_CACHE_FILEPATH, READ_MODE) as tle_cache_file:
        tle_cache = pickle.load(tle_cache_file)
        return tle_cache

def save_tle_cache_in_disk(tle_cache):
    WRITE_MODE = 'wb'
    with open(TLE_CACHE_FILEPATH, WRITE_MODE) as tle_cache_file:
        pickle.dump(tle_cache, tle_cache_file)

def get_and_update_tle_from_disk(norad_id):
    assert(isinstance(norad_id, int))

    LINE1, LINE2 = 'line1', 'line2'

    now = datetime.now(tz=timezone.utc)
    should_download_tle = True

    tle_value = None

    try:
        tle_cache = get_tle_cache_from_disk()
        if norad_id in tle_cache:
            tle_value = tle_cache[norad_id]
            time_delta = now - tle_value[DOWNLOADED_AT_KEY]
            if time_delta.total_seconds() < TLE_UPDATE_TIME:
                should_download_tle = False
    except FileNotFoundError:
        tle_cache = {}

    is_internet_on = internet_on()
    if should_download_tle and is_internet_on:
        print('Downloading new TLE for NORAD={}'.format(norad_id))
        tle = fetch_new_tle(norad=norad_id)
        tle_value = {
            DOWNLOADED_AT_KEY: now,
            LINE1: tle.tle_line1,
            LINE2: tle.tle_line2,
        }

        tle_cache[norad_id] = tle_value
        save_tle_cache_in_disk(tle_cache)
    elif should_download_tle and not is_internet_on:
        print('Internet is off: cant dowload new TLE. Trying to get from disk')

    assert(tle_cache, 'Cant fetch TLE: TLE not found on disk and internet '
                      'is off')

    assert(tle_value, 'Cant fetch TLE: TLE not found on disk and internet '
                      'is off')
    return tle_value[LINE1], tle_value[LINE2]


def internet_on():
    try:
        response = urlopen('https://www.n2yo.com/', timeout=10)
        return True
    except:
        return False

def save_or_update_tle_in_db(tle):
    assert(len(tle) == 2)

if __name__ == '__main__':
    norad = 25544
    print('get_and_update_tle_from_disk = {}'.format(get_and_update_tle_from_disk))


