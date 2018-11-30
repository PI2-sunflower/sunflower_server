from satellite.tle_getter import get_and_update_tle_from_disk


def set_all_tles():
    MAX_NORAD = 50000

    for norad in range(1, MAX_NORAD + 1):
        try:
            get_and_update_tle_from_disk(norad)
        except:
            pass
