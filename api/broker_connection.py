import os

import paho.mqtt.client as mqtt

from time import sleep, time
from threading import Thread

MQTT_HOST = "localhost"  # os.environ.get('MQTT_HOST', "localhost")
print("=" * 80)
print(f"HOST: {MQTT_HOST}")
print("=" * 80)


class MQTTConnection:
    instance = None

    def __new__(cls):
        if not MQTTConnection.instance:
            MQTTConnection.instance = MQTTConnection.__MQTTConnection()

        return MQTTConnection.instance

    class __MQTTConnection:
        __slots__ = (
            "_status",
            "_status_process",
            "_last_status_time",
            "flag_connected",
            "mqtt_client",
            "logger",
        )

        def __init__(self, logger=None):
            self._status = "dead"
            self._status_process = None
            self._last_status_time = 0
            self.flag_connected = 0
            self.mqtt_client = mqtt.Client("C1")
            self.logger = logger

            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            self.mqtt_client.on_message = self._on_message

        def connect(self):
            def keep_alive():
                if self.flag_connected == 0:
                    print("*** CONNECTING TO BROKER ***")
                    self.mqtt_client.connect(MQTT_HOST, 1883, 60)
                    self.mqtt_client.loop_forever()

            process = Thread(target=keep_alive)
            process.start()

        def publish(self, topic="", command=""):
            info = self.mqtt_client.publish(topic=topic, payload=command, qos=1)
            info.wait_for_publish()

        def _on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                print("CONNECTED")
                self.flag_connected = 1
                self.mqtt_client.subscribe("status")
            else:
                print(self._refused_connection(rc))

        def _on_disconnect(self, client, userdata, rc):
            self.flag_connected = 0
            print("DICONNECTED")

        def _on_message(self, client, userdata, message):
            received = str(message.payload.decode("utf-8"))

            if message.topic == "status":
                self._status_check(received)

        def _refused_connection(self, rc: int) -> str:
            msg = ""

            if rc == 1:
                msg = "incorrect protocol version"
            elif rc == 2:
                msg = "invalid client identifier"
            elif rc == 3:
                msg = "server unavailable"
            elif rc == 4:
                msg = "bad username or password"
            elif rc == 5:
                msg = "not authorised"
            else:
                msg = ""

            return "Connection refused - {}".format(msg)

        def _status_check(self, message):
            self._status = message
            self._last_status_time = time()

            def kill_after_30_seconds():
                sleep(30)
                self._status_process = None
                self._status_check("dead")

            if self._status_process is None:
                self._status_process = Thread(target=kill_after_30_seconds)
                self._status_process.start()

        @property
        def status(self):
            return self._status
