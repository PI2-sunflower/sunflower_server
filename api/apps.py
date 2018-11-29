import sys


from django.apps import AppConfig

from api.broker_connection import MQTTConnection


broker_connection_started = False


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        if "runserver" in sys.argv:
            self._connect_to_broker()

    def _connect_to_broker(self):
        global broker_connection_started

        if not broker_connection_started:
            connection = MQTTConnection()
            connection.connect()

