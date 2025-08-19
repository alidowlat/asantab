from django.db import models
import random
from django.urls import reverse

STATUS_CHOICES = [
    ('pending', 'در حال بررسی'),
    ('accepted', 'تایید شده'),
    ('rejected', 'رد شده'),
    ('completed', 'تکمیل شده'),
]

ORDER_STATUS_STYLES = {
    'pending': {
        'color': 'text-yellow-500',
        'bg': 'bg-yellow-500',
        'icon': 'i-ic-baseline-pending-actions ',
        'progress': 30
    },
    'accepted': {
        'color': 'text-success',
        'bg': 'bg-success',
        'icon': 'i-lucide-thumbs-up',
        'progress': 60
    },
    'rejected': {
        'color': 'text-red-600',
        'bg': 'bg-red-500',
        'icon': 'i-lucide-circle-x',
        'progress': 100
    },
    'completed': {
        'color': 'text-teal-500',
        'bg': 'bg-teal-500',
        'icon': 'i-lucide-circle-check',
        'progress': 100
    }
}


class Order(models.Model):
    tracking_code = models.CharField(
        max_length=6,
        unique=True,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='کاربر'
    )
    provider = models.ForeignKey(
        'accounts.Provider',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_orders',
        verbose_name='ارائه دهنده'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت سفارش'
    )
    wallet_transaction = models.ForeignKey(
        'wallet.WalletTransaction',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='تراکنش ولت مرتبط'
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ پرداخت'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='دلیل رد شدن'
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name='پرداخت شده؟'
    )
    discount_code = models.ForeignKey(
        'discounts.DiscountCode',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='کد تخفیف'
    )

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def generate_tracking_code(self):
        while True:
            code = str(random.randint(100000, 999999))
            if not Order.objects.filter(tracking_code=code).exists():
                return code

    def get_status_style(self):
        return ORDER_STATUS_STYLES.get(self.status, {})

    def __str__(self):
        return f'{self.is_paid} | {self.user} - {self.provider} --> {self.status}'

    def save(self, *args, **kwargs):
        if self.rejection_reason and self.status != 'rejected':
            self.status = 'rejected'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'orders'
