import sys
from threading import Thread


from django.apps import AppConfig

from api.mqtt_broker import mqtt_start_connection

process = Thread(target=mqtt_start_connection)

broker_connection_started = False


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        if "runserver" in sys.argv:
            self._connect_to_broker()

    def _connect_to_broker(self):
        global broker_connection_started

        if not broker_connection_started:
            process.start()
            broker_connection_started = True
