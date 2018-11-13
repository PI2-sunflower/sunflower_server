from django.db import models
from django.utils import timezone


class Tle(models.Model):
    norad = models.IntegerField(primary_key=True)
    line1 = models.CharField(max_length=69)
    line2 = models.CharField(max_length=69)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '(norad: {}, updated_at: {})'.format(self.norad, self.updated_at)
