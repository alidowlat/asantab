from django.db import models

from wallet.models.abstracts import TimeStampedModel, AmountModel, PSPReferenceMixin


class PaymentGateway(models.Model):
    name = models.CharField(max_length=35, verbose_name="نام درگاه")
    merchant_id = models.CharField(max_length=120, unique=True, verbose_name="شناسه فروشنده")
    callback_url = models.URLField(verbose_name="آدرس بازگشت بعد از پرداخت")
    is_active = models.BooleanField(default=True, verbose_name="فعال است؟")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateway'
        db_table = 'payment_gateway'


class PaymentTransaction(TimeStampedModel, AmountModel, PSPReferenceMixin):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "شارژ"
        WITHDRAWAL = "withdrawal", "برداشت"
        REFUND = "refund", "بازگشت"

    wallet = models.ForeignKey('wallet.Wallet', on_delete=models.CASCADE, related_name="payment_transactions", verbose_name="کیف پول")
    gateway = models.ForeignKey('wallet.PaymentGateway', on_delete=models.PROTECT, related_name="transactions",
                                verbose_name="درگاه پرداخت")
    type = models.CharField(max_length=20, choices=TransactionType.choices, verbose_name="نوع تراکنش")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    def __str__(self):
        return f"{self.wallet.user} - {self.type} - {self.amount} Toman"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        db_table = 'payment_transactions'
