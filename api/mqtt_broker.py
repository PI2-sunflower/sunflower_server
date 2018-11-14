import os

import paho.mqtt.client as mqtt
from time import sleep

from sunflower_ll.translator import Translator

# 10.0.0.222
MQTT_HOST = os.environ.get('MQTT_HOST', "localhost")
#connection_topic = "OLA"

print("="*80)
print(f"HOST: {MQTT_HOST}")
print("="*80)


# def on_connect(client, userdata, flags, rc):
#    if rc == 0:
#        print('connecting')
#        client.connected_flag = True
#        client.publish(connection_topic, 1, retain=True)
#    else:
#        client.bad_connection_flag = True


#client = mqtt.Client("C1")

#client.connected_flag = False
#client.on_connect = on_connect


# def start_connection():
#    print("START MQTT CONNECTION")
#    client.connect(MQTT_HOST, 1883, 60)

# while not client.connected_flag:  # wait in loop
#    print("In wait loop")
#    sleep(1)


# def get_client():
#    return client


class AnntenaCommand:
    __slots__ = ('command', 'tr', 'mqtt_client', 'params',)

    def __init__(self, command, params=None):
        self.command = command
        self.params = params
        self.mqtt_client = mqtt.Client("C1")
        self.tr = Translator()

    def execute(self):
        if self.command == "move_axis":
            print("="*80)
            print(self.params)
            print("="*80)

            self.tr.set_axis_angles(self.params)
            output = self.tr.move_axis()
        else:
            output = self._get_broker_output(self.command)

        try:
            self.mqtt_client.connect(MQTT_HOST, 1883, 60)
            self.mqtt_client.publish(output["topic"], output["command"])
            self.mqtt_client.disconnect()

            return True
        except Exception as e:
            return False

    def _get_broker_output(self, command):
        action = getattr(self.tr, command, None)
        broker_output = dict()

        if action is not None:
            broker_output = action()

        return broker_output
