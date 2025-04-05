import os
import uuid
from datetime import datetime

import requests
from django.apps import apps
from django.conf import settings


def take_photo():
    """Получает фото с Flask сервера и сохраняет в media/photos/"""

    flask_api_url = "http://192.168.0.106:5000/take_photo"

    response = requests.get(flask_api_url)

    if response.status_code == 200:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
        filepath = os.path.join(settings.MEDIA_ROOT, "photos", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as photo_file:
            photo_file.write(response.content)

        Camera = apps.get_model("devices", "Camera")
        camera, _ = Camera.objects.get_or_create(id=1)
        camera.last_photo.name = f"photos/{filename}"
        camera.save()

        return filepath
    else:
        raise Exception("Ошибка при получении фото с Flask сервера")
