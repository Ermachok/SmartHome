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


    week_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    now = datetime.now(pytz.timezone('Europe/Moscow'))
    current_time = now.time()
    current_day = now.weekday()

    current_day_str = week_days[current_day]

    logger.info(f"Текущее время: {current_time.hour}:{current_time.minute}, День: {current_day_str}")

    all_schedules = LightSchedule.objects.all()
    logger.info(f"Всего записей в LightSchedule: {all_schedules.count()}")
    for schedule in all_schedules:
        days_str = ", ".join([day for day in schedule.days])
        logger.info(
            f"ID {schedule.id} | Время: {schedule.time.hour}:{schedule.time.minute} | Дни: {days_str} | Активно: {schedule.is_active}")

    active_schedules = LightSchedule.objects.filter(
        is_active=True,
        time__hour=current_time.hour,
        time__minute=current_time.minute
    )

    logger.info(f"Найдено {active_schedules.count()} активных расписаний.")

    for schedule in active_schedules:
        logger.info(f"Проверка расписания ID {schedule.id}: {schedule.days}")
        logger.info(f"Cейчас {current_day_str}")
        if current_day_str in schedule.days:
            logger.info(f"Расписание ID {schedule.id} подходит. Включаем светильник.")

            from .views import lamp
            if lamp:
                lamp.on(mode=1)
                Light.objects.update_or_create(defaults={'is_on': True})
                logger.info("Светильник включен.")
            else:
                logger.warning("Объект lamp не найден, невозможно включить свет.")
        else:
            logger.info(f"Расписание ID {schedule.id} не сработало, день не совпадает.")

    logger.info("Задача check_light_schedules завершена.")