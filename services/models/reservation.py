from django.db import models


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        verbose_name='خریدار',
        related_name='reservations'
    )
    schedule = models.ForeignKey(
        'services.Schedule',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='زمان‌بندی رزرو',
        null=True, blank=True
    )
    option = models.ForeignKey(
        'services.Option',
        on_delete=models.CASCADE,
        verbose_name='نوع تبلیغ',
        related_name='reservations'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        verbose_name = 'رزرو'
        verbose_name_plural = 'رزروها'
        db_table = 'reservations'
        ordering = ['-created_at']
        unique_together = ('user', 'schedule', 'option')

    def __str__(self):
        return f"{self.user} - {self.schedule.date} - {self.schedule.service.title}"

    def display_reserve_date(self):
        return self.schedule.date