import logging
from celery import shared_task
from django.apps import apps
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


@shared_task
def check_light_schedules():
    """ Проверяет расписание и включает светильник. """
    logger.info("Запуск задачи check_light_schedules...")

    Light = apps.get_model('devices', 'Light')
    LightSchedule = apps.get_model('devices', 'LightSchedule')

    now = datetime.now(pytz.timezone('Europe/Moscow'))

    all_schedules = LightSchedule.objects.all()
    logger.info(f"Всего записей в LightSchedule: {all_schedules.count()}")

    for schedule in all_schedules:
        if schedule.should_trigger_now(now):
            logger.info(f"Расписание ID {schedule.id} подходит. Включаем светильник.")

            from .views import lamp
            if lamp:
                lamp.on(mode=1)
                Light.objects.update_or_create(defaults={'is_on': True})
                logger.info("Светильник включен.")
            else:
                logger.warning("Светильник не найден, невозможно включить свет.")

    logger.info("Задача check_light_schedules завершена.")

