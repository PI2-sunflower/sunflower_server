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

