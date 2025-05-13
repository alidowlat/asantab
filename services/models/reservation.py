from datetime import timezone
from django.core.exceptions import ValidationError
from django.db import models


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('confirmed', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='خریدار')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, verbose_name='خدمت')
    option = models.ForeignKey('services.Option', on_delete=models.CASCADE, verbose_name='نوع تبلیغ')
    reserved_date = models.DateField(verbose_name='تاریخ رزرو')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        verbose_name = 'reservation'
        verbose_name_plural = 'reservations'
        db_table = 'reservations'
        ordering = ['-reserved_date']

    def __str__(self):
        return f"{self.service.title} - {self.reserved_date} - {self.user}"
