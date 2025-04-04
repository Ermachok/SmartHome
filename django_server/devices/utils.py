import os
import uuid
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

    # mock
    with open(filepath, "wb") as f:
        f.write(b"\x00" * 1024)

    camera, _ = Camera.objects.get_or_create(id=1)
    camera.last_photo.name = f"photos/{filename}"
    camera.save()

    return filepath
