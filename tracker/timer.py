from threading import Thread
from time import sleep


class TrackTimer:
    instance = None

    def __new__(cls):
        if not TrackTimer.instance:
            TrackTimer.instance = TrackTimer.__TrackTimer()

        return TrackTimer.instance


    class __TrackTimer:
        def __init__(self):
            self._is_active = False

        def set_data(self, angle_1, angle_2, time):
            self.angle_1 = angle_1
            self.angle_2 = angle_2
            self.time = time

        def start(self):
            self._is_active = True

            def timer():
                while self._is_active:
                    print("Ola")

            process = Thread(target=timer)
            process.start()

        def stop(self):
            self._is_active = False
        
        @property
        def is_active():
            return self._is_active
