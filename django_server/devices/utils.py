import os
import uuid
import picamera
from datetime import datetime
from django.conf import settings
from django.apps import apps


def take_photo():
    """Делает фото и сохраняет в media/photos/"""
    Camera = apps.get_model("devices", "Camera")

    filename = (
        f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
    )
    filepath = os.path.join(settings.MEDIA_ROOT, "photos", filename)

    with picamera.PICamera() as camera:
        camera.resolution = (1024, 768)
        camera.capture(filepath)

    camera, _ = Camera.objects.get_or_create(id=1)
    camera.last_photo.name = f"photos/{filename}"
    camera.save()

    return filepath
