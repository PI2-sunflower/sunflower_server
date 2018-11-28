import os

import paho.mqtt.client as mqtt
from time import sleep
from typing import Tuple
from threading import Thread
from collections import deque

from sunflower_ll.translator import Translator

# 10.0.0.222
MQTT_HOST = "localhost"  # os.environ.get('MQTT_HOST', "localhost")
# connection_topic = "OLA"

print("=" * 80)
print(f"HOST: {MQTT_HOST}")
print("=" * 80)

flag_connected = 0


def on_connect(client, userdata, flags, rc):
    global flag_connected

    # print("Connected with result code " + str(rc))
    flag_connected = 1


def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    pass


mqtt_client = mqtt.Client("C1")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def mqtt_start_connection():
    global flag_connected
    global mqtt_client

    if flag_connected == 0:
        print("*** CONNECTING TO BROKER ***")
        mqtt_client.connect(MQTT_HOST, 1883, 60)
        mqtt_client.loop_forever()


# process = Thread(target=mqtt_start_connection)
# process.start()


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


class AnntenaCommand:
    __slots__ = ("command", "tr", "mqtt_client", "params")

    def __init__(self, command, params=None):
        self.command = command
        self.params = params
        self.mqtt_client = mqtt.Client("C1")
        self.tr = Translator()

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
            # self.mqtt_client.connect(MQTT_HOST, 1883, 60)
            global mqtt_client

            print("SENT TO BROKER")
            print("TOPIC: {}\n COMMAND: {}".format(output["topic"], output["command"]))

            CommandHistory().add_to_history(output["topic"], output["command"])

            mqtt_client.publish(output["topic"], output["command"])
            # mqtt_client.disconnect()

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
