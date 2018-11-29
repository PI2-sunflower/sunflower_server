import os

import paho.mqtt.client as mqtt
from time import sleep
from typing import Tuple
from threading import Thread
from collections import deque

from sunflower_ll.translator import Translator

from api.broker_connection import MQTTConnection


class CommandHistory:
    instance = None
    MAX_HISTORY = 25

    class __CommandHistory:
        __slots__ = ("_history",)

        def __init__(self):
            self._history = deque()

        def add_to_history(self, topic, command):
            mqtt_code = {"topic": topic, "command": command}

            self._history.appendleft(mqtt_code)

            if len(self._history) > CommandHistory.MAX_HISTORY:
                self._history.pop()

        @property
        def history(self):
            return list(self._history)

    def __new__(cls):
        if not CommandHistory.instance:
            CommandHistory.instance = CommandHistory.__CommandHistory()

        return CommandHistory.instance


def arm_data_instance():
    from tracker.data import arm_data_instance  as adi
    return adi()


class AnntenaCommand:
    __slots__ = ("command", "tr", "params", "mqtt")

    def __init__(self, command, params=None):
        arm_data = arm_data_instance()

        self.command = command
        self.params = params
        self.tr = Translator()
        self.mqtt = MQTTConnection()

        self.tr.set_operation_mode(arm_data.operation)
        self.tr.set_angle_error_offset({
            "angle_1": arm_data.error_angle_1,
            "angle_2": arm_data.error_angle_2,
            "angle_3": arm_data.error_angle_3,
        })

    def execute(self) -> Tuple[bool, str]:
        if self.command == "move_axis":
            invalid_angles = self.tr.validate_axis(
                {**{"angle_1": 0, "angle_2": 0, "angle_3": 0}, **self.params}
            )

            if invalid_angles == 1:
                message = "Invalid angles"
                self.register_fail(message)
                return (False, message)

            self.tr.set_axis_angles(self.params)
            (err, output) = self.tr.move_axis()
        else:
            output = self._get_broker_output(self.command)

        try:
            print("SENT TO BROKER")
            print("TOPIC: {}\n COMMAND: {}".format(output["topic"], output["command"]))

            CommandHistory().add_to_history(output["topic"], output["command"])

            self.mqtt.publish(output["topic"], output["command"])

            return (True, "")
        except Exception as e:
            message = "Could not send command to broker"
            self.register_fail(message)

            return (False, message)

    def _get_broker_output(self, command):
        action = getattr(self.tr, command, None)
        broker_output = dict()

        if action is not None:
            broker_output = action()

        return broker_output

    def register_fail(self, message):
        CommandHistory().add_to_history("FAIL", message)
