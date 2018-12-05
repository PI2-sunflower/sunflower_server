from threading import Thread
from time import sleep

from api.mqtt_broker import AnntenaCommand


class TrackTimer:
    instance = None

    def __new__(cls):
        if not TrackTimer.instance:
            TrackTimer.instance = TrackTimer.__TrackTimer()

        return TrackTimer.instance

    class __TrackTimer:
        def __init__(self):
            self._is_active = False

        def set_data(self, start_angle, end_angle, time):
            self.start_angle = start_angle
            self.end_angle = end_angle
            self.time = time
            # self.current_angle = start_angle

        def start(self):
            self._is_active = True

            def timer():
                step = self.step
                current_time = 0
                current_angle = self.start_angle

                angles = {"angle_1": 0, "angle_2": 5, "angle_3": 0}

                while self._is_active:
                    print("TIMER at: {} seconds".format(current_time))
                    print("Angle at: {}".format(current_angle))

                    angles["angle_1"] = current_angle
                    command = AnntenaCommand("move_axis", angles)
                    command.execute()

                    current_time += 1
                    current_angle += step

                    if current_time > self.time:
                        self.stop()

                    sleep(1)

            process = Thread(target=timer)
            process.start()

        def stop(self):
            self._is_active = False

        @property
        def is_active(self):
            return self._is_active

        @property
        def step(self):
            value = (self.end_angle - self.start_angle) / self.time
            return value
