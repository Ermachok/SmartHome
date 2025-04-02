import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_home.settings")

app = Celery("smart_home")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check_light_every_minute": {
        "task": "devices.tasks.check_light_schedules",
        "schedule": crontab(minute="*"),
    },
}
