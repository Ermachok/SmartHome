from django.db import models
from datetime import datetime
import pytz


class Light(models.Model):
    is_on = models.BooleanField(default=False)
    brightness = models.IntegerField(default=100)


class Camera(models.Model):
    is_recording = models.BooleanField(default=False)
    last_photo = models.ImageField(upload_to="photos/", null=True, blank=True)


class LightSchedule(models.Model):
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
    days = models.JSONField(
        default=list,
        verbose_name="Дни недели",
        help_text="Список дней, когда должно срабатывать расписание"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Включено ли это расписание"
    )

    class Meta:
        verbose_name = "Расписание света"
        verbose_name_plural = "Расписания света"
        ordering = ['time']

    def should_trigger_now(self, check_datetime=None):
        """
        Проверяет, должно ли сработать расписание в текущий момент времени.
        Можно передать конкретное время для проверки (для тестирования).
        """
        if not self.is_active:
            return False

        now = check_datetime if check_datetime else datetime.now(pytz.timezone('Europe/Moscow'))
        current_time = now.time()
        current_day = now.strftime('%a').lower()

        time_matches = (
                self.time.hour == current_time.hour and
                self.time.minute == current_time.minute
        )

        return time_matches and current_day in self.days

    def get_active_schedules_now(cls, check_datetime=None):
        """
        Классовый метод для получения всех активных расписаний, которые должны сработать сейчас.
        """
        now = check_datetime if check_datetime else datetime.now(pytz.timezone('Europe/Moscow'))
        current_time = now.time()
        current_day = now.strftime('%a').lower()

        return cls.objects.filter(
            is_active=True,
            time__hour=current_time.hour,
            time__minute=current_time.minute,
            days__contains=[current_day]
        )

    def __str__(self):
        day_names = dict(self.DAYS_OF_WEEK)
        days_display = ', '.join([day_names.get(day, day) for day in self.days])
        return f"Расписание на {self.time.strftime('%H:%M')} ({days_display})"
