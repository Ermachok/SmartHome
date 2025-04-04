import logging
from datetime import datetime

import pytz
from django.apps import apps
from utils import take_photo
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_schedules():
    """Проверяет расписания и выполняет нужные действия (включение света, снимки камеры)."""
    logger.info("Запуск задачи check_schedules...")

    Light = apps.get_model("devices", "Light")
    LightSchedule = apps.get_model("devices", "LightSchedule")
    CameraSchedule = apps.get_model("devices", "CameraSchedule")

    now = datetime.now(pytz.timezone("Europe/Moscow"))

    for schedule in LightSchedule.objects.all():
        if schedule.should_trigger_now(now):
            logger.info(f"Включаем светильник по расписанию ID {schedule.id}")
            from .views import lamp

            if lamp:
                lamp.on(mode=1)
                Light.objects.update_or_create(defaults={"is_on": True})
            else:
                logger.warning("lamp не найден, невозможно включить свет.")

    logger.info(now)
    for schedule in CameraSchedule.objects.all():
        if schedule.should_trigger_now(now):
            logger.info(f"Делаем снимок по расписанию ID {schedule.id}")
            take_photo()

    logger.info("Задача check_schedules завершена.")
