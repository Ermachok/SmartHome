from datetime import datetime

import pytz
from django.db import models


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
        help_text="Список дней, когда должно срабатывать расписание",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Активно", help_text="Включено ли это расписание"
    )

    def should_trigger_now(self, check_datetime=None):
        """
        Проверяет, должно ли сработать расписание в текущий момент времени.
        Можно передать конкретное время для тестирования.
        """
        if not self.is_active:
            return False

        week_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        now = check_datetime

        current_time = now.time()
        current_day_str = week_days[now.weekday()]

        time_matches = (
            self.time.hour == current_time.hour
            and self.time.minute == current_time.minute
        )

        return time_matches and current_day_str in self.days

    def __str__(self):
        day_names = dict(self.DAYS_OF_WEEK)
        days_display = ", ".join(
            [day_names.get(self.DAYS_OF_WEEK[day][0], str(day)) for day in self.days]
        )
        return f"Расписание на {self.time.strftime('%H:%M')} ({days_display})"
