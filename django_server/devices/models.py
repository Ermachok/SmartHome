import logging
from datetime import datetime
import pytz
from django.db import models

logger = logging.getLogger(__name__)


class Light(models.Model):
    is_on = models.BooleanField(default=False)
    brightness = models.IntegerField(default=100)


class Camera(models.Model):
    is_recording = models.BooleanField(default=False)
    last_photo = models.ImageField(upload_to="photos/", null=True, blank=True)


class BaseSchedule(models.Model):
    DAYS_OF_WEEK = [
        ("mon", "Понедельник"),
        ("tue", "Вторник"),
        ("wed", "Среда"),
        ("thu", "Четверг"),
        ("fri", "Пятница"),
        ("sat", "Суббота"),
        ("sun", "Воскресенье"),
    ]

    time = models.TimeField(verbose_name="Время срабатывания")
    days = models.JSONField(default=list, verbose_name="Дни недели")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        abstract = True

    def should_trigger_now(self, check_datetime=None):
        if not self.is_active:
            return False

        now = check_datetime or datetime.now(pytz.timezone("Europe/Moscow"))
        current_time = now.time()
        current_day = now.strftime("%a").lower()

        time_matches = (
            self.time.hour == current_time.hour
            and self.time.minute == current_time.minute
        )
        day_matches = current_day in self.days

        if time_matches and day_matches:
            logger.info(f"Расписание ID {self.id} должно сработать!")
        # else:
        # logger.info(
        #     f"Расписание ID {self.id} НЕ срабатывает (совпадение по времени: {time_matches}, по дню: {day_matches})")

        return time_matches and day_matches


class LightSchedule(BaseSchedule):
    pass


class CameraSchedule(BaseSchedule):
    pass
