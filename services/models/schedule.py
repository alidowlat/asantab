from django.db import models


class Schedule(models.Model):
    WEEK_DAYS = [
        (0, 'شنبه'),
        (1, 'یک‌شنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنج‌شنبه'),
        (6, 'جمعه'),
    ]

    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='schedules', verbose_name='سرویس')
    weekday = models.PositiveSmallIntegerField(choices=WEEK_DAYS, verbose_name='روز های هفته')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    capacity = models.PositiveIntegerField(default=0, verbose_name='ظرفیت')

    class Meta:
        unique_together = ('service', 'weekday')
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        db_table = "schedules"

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.service.title}"
