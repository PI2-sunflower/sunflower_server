from django.db import models


class ArmPosition(models.Model):
    latitude = models.FloatField(default=0.0, blank=False, null=False)
    longitude = models.FloatField(default=0.0, blank=False, null=False)
    altitude = models.FloatField(default=0.0, blank=False, null=False)
    magnetometer = models.FloatField(default=0.0, blank=False, null=False)
    engine_speed = models.PositiveIntegerField(default=0.0, blank=False, null=False)


class ArmData(models.Model):
    operation = models.CharField(max_length=1, blank=False, null=False, default="a")
    error_angle_1 = models.FloatField(default=0.0, blank=False, null=False)
    error_angle_2 = models.FloatField(default=0.0, blank=False, null=False)
    error_angle_3 = models.FloatField(default=0.0, blank=False, null=False)
