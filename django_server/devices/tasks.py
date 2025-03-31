from celery import shared_task
from django.apps import apps
from datetime import datetime
import pytz


@shared_task
def check_light_schedules():
    """ Проверяет расписание и включает светильник. """
    Light = apps.get_model('devices', 'Light')
    LightSchedule = apps.get_model('devices', 'LightSchedule')

    now = datetime.now(pytz.timezone('Europe/Moscow'))
    current_time = now.time()
    current_day = now.strftime('%a').lower()

    active_schedules = LightSchedule.objects.filter(
        is_active=True,
        time__hour=current_time.hour,
        time__minute=current_time.minute
    )

    for schedule in active_schedules:
        if current_day in schedule.days:
            from .views import lamp
            if lamp:
                lamp.turn_on()
                Light.objects.update_or_create(defaults={'is_on': True})
