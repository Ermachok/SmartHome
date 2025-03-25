from django.db import models


class Light(models.Model):
    is_on = models.BooleanField(default=False)
    brightness = models.IntegerField(default=100)


class Camera(models.Model):
    is_recording = models.BooleanField(default=False)
    last_photo = models.ImageField(upload_to='photos/', null=True, blank=True)
