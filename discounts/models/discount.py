from django.core.exceptions import ValidationError
from django.db import models
from datetime import date


class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='کد تخفیف')
    amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='مقدار تخفیف (تومان)')
    percent = models.PositiveIntegerField(null=True, blank=True, verbose_name='درصد تخفیف')
    expiration_date = models.DateField(verbose_name='تاریخ انقضا')

    def clean(self):
        if bool(self.amount) == bool(self.percent):
            raise ValidationError("فقط یکی از فیلدهای مقدار تخفیف یا درصد تخفیف باید تنظیم شود.")

    @property
    def type(self):
        if self.amount:
            return 'amount'
        elif self.percent:
            return 'percent'
        return 'none'

    def is_valid_for_user(self, user):
        if self.expiration_date < date.today():
            return False
        return not DiscountCodeUser.objects.filter(user=user, discount_code=self).exists()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Discount Code'
        verbose_name_plural = 'Discount Codes'
        db_table = 'discount_codes'

class DiscountCodeUser(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='کاربر')
    discount_code = models.ForeignKey(DiscountCode, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='کد تخفیف')
    redeem_at = models.DateTimeField(auto_now_add=True, verbose_name='استفاده شده در تاریخ')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت کرده؟')

    class Meta:
        unique_together = ('user', 'discount_code')
        verbose_name = 'Discount Code User'
        verbose_name_plural = 'Discount Code Users'
        db_table = 'discount_code_users'
