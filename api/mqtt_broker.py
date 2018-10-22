import os

import paho.mqtt.client as mqtt
from time import sleep

# 10.0.0.222
MQTT_HOST = os.environ.get('MQTT_HOST', "localhost")
connection_topic = "OLA"

print("="*80)
print(f"HOST: {MQTT_HOST}")
print("="*80)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('connecting')
        client.connected_flag = True
        client.publish(connection_topic, 1, retain=True)
    else:
        client.bad_connection_flag = True


client = mqtt.Client("C1")

client.connected_flag = False
client.on_connect = on_connect


def start_connection():
    print("START MQTT CONNECTION")
    client.connect(MQTT_HOST, 1883, 60)

    # while not client.connected_flag:  # wait in loop
    #    print("In wait loop")
    #    sleep(1)


def get_client():
    return client
