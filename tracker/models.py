from django.db import models


class ArmPosition(models.Model):
    latitude = models.FloatField(default=0.0, blank=False, null=False)
    longitude = models.FloatField(default=0.0, blank=False, null=False)
    altitude = models.FloatField(default=0.0, blank=False, null=False)
    magnetometer = models.FloatField(default=0.0, blank=False, null=False)
    engine_speed = models.PositiveIntegerField(default=0.0, blank=False, null=False)
