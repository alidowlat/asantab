from django.db import models

STATUS_CHOICES = [
    ('pending', 'در حال بررسی'),
    ('accepted', 'تایید شده'),
    ('rejected', 'رد شده'),
    ('completed', 'تکمیل شده'),
]


class Order(models.Model):
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=
        'تاریخ ثبت')
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=
        'تاریخ بروزرسانی')
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

    def __str__(self):
        return f'{self.is_paid} | {self.user} - {self.provider} --> {self.status}'

    def save(self, *args, **kwargs):
        if self.rejection_reason and self.status != 'rejected':
            self.status = 'rejected'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'orders'
