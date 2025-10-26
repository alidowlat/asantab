from django.db import models


class Schedule(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='schedules', verbose_name='سرویس')
    date = models.DateField(null=True, blank=True, verbose_name='تاریخ')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    capacity = models.PositiveIntegerField(default=0, verbose_name='ظرفیت')

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        db_table = "schedules"

    def __str__(self):
        day = self.date.strftime('%A')
        return f"{self.date} ({day})"

    @property
    def used_capacity(self):
        return sum(
            item.count
            for item in self.orderitem_set.filter(vendor_order__status=["pending", "accepted"])
        )

    @property
    def remaining_capacity(self):
        return self.capacity - self.used_capacity

    def display_date(self):
        if self.date:
            return self.date
        return None
