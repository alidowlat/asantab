from django.core.exceptions import ValidationError
from django.db import models, transaction
from wallet.models import WalletTransaction, Wallet
from wallet.models.abstracts import AmountModel, PSPReferenceMixin, TimeStampedModel


class WithdrawalRequest(TimeStampedModel, AmountModel):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
        ("paid", "پرداخت شده"),
    ]

    wallet = models.ForeignKey('wallet.Wallet', on_delete=models.CASCADE, related_name="withdrawal_requests", verbose_name='کیف پول')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name='وضعیت')
    bank_account = models.ForeignKey("accounts.BankAccount", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="withdrawals", verbose_name='حساب بانکی')
    sheba_number = models.CharField(max_length=24, null=True, blank=True, verbose_name="شماره شبا")
    card_number = models.CharField(max_length=16, null=True, blank=True, verbose_name="شماره کارت")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")

    def __str__(self):
        return f"{self.wallet.user} - {self.get_status_display()} >>> {self.amount}"

    def save(self, *args, **kwargs):
        if self.bank_account:
            self.sheba_number = self.bank_account.sheba_number
            self.card_number = self.bank_account.card_number

        if not (self.sheba_number and self.card_number):
            raise ValidationError("باید شماره شبا و کارت یا حساب بانکی معتبر وارد شود.")

        super().save(*args, **kwargs)

    @transaction.atomic
    def mark_as_approved(self, reference_id=None):
        if self.status != "pending":
            return
        self.status = "approved"
        self.save()

        # idempotent withdraw
        if reference_id and not WalletTransaction.objects.filter(reference_id=reference_id,
                                                                 type=WalletTransaction.TransactionType.WITHDRAW,
                                                                 wallet=self.wallet).exists():
            with transaction.atomic():
                wallet = self.wallet
                wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
                wallet.withdraw(
                    amount=self.amount,
                    description=f"Withdrawal approved: {self.id}",
                    reference_id=reference_id
                )

    @transaction.atomic
    def mark_as_paid(self, reference_id=None):
        if self.status == "paid":
            return
        self.status = "paid"
        self.save()

    @transaction.atomic
    def mark_rejected(self):
        if self.status == "rejected":
            return
        self.status = "rejected"
        self.save()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Withdrawal Request'
        verbose_name_plural = 'Withdrawal Requests'
        db_table = 'withdrawal_requests'


class DepositRequest(TimeStampedModel, PSPReferenceMixin):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("canceled", "لغو شده"),
    ]

    wallet = models.ForeignKey('wallet.Wallet', on_delete=models.CASCADE, related_name="deposit_requests", verbose_name='کیف پول')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="مبلغ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت")
    gateway = models.ForeignKey("wallet.PaymentGateway", on_delete=models.PROTECT, related_name="deposits",
                                verbose_name="درگاه پرداخت")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")

    @transaction.atomic
    def mark_as_paid(self, ref_id=None, tracking_code=None):
        if self.status == "paid":
            return
        self.status = "paid"
        if ref_id:
            self.ref_id = ref_id
        if tracking_code:
            self.tracking_code = tracking_code
        self.save()

        if not WalletTransaction.objects.filter(reference_id=self.ref_id, type=WalletTransaction.TransactionType.DEPOSIT).exists():
            self.wallet.deposit(
                amount=self.amount,
                description=f"Deposit via Gateway: {self.gateway.name}",
                reference_id=self.ref_id
            )

    @transaction.atomic
    def mark_failed(self, ref_id=None):
        self.status = "failed"
        if ref_id:
            self.ref_id = ref_id
        self.save()

    @transaction.atomic
    def mark_canceled(self):
        self.status = "canceled"
        self.save()

    def __str__(self):
        return f"{self.wallet.user} - {self.amount} Toman - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deposit Request'
        verbose_name_plural = 'Deposit Requests'
        db_table = 'deposit_requests'
