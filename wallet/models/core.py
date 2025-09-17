import secrets
from decimal import Decimal, ROUND_DOWN
from django.db import models, transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from wallet.models.abstracts import TimeStampedModel, AmountModel
from django.db.models import F

User = get_user_model()


class Wallet(TimeStampedModel):
    ROLE_CHOICES = [
        ("admin", "مدیر"),
        ("staff", "کارشناس"),
        ("provider", "فروشنده"),
        ("user", "کاربر"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet", verbose_name="کاربر")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="نقش")
    balance = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="موجودی آزاد")
    frozen_balance = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="موجودی معلق")
    secret_code = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.secret_code:
            self.secret_code = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def can_withdraw(self, amount: Decimal):
        return self.balance >= amount and amount >= settings.MIN_WITHDRAW_AMOUNT

    def deposit(self, amount: Decimal, description="", reference_id=None):
        if reference_id and WalletTransaction.objects.filter(reference_id=reference_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=reference_id, wallet=self)
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.DEPOSIT,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def withdraw(self, amount: Decimal, description="", reference_id=None):
        if reference_id and WalletTransaction.objects.filter(reference_id=reference_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=reference_id, wallet=self)

        commission_rule = CommissionRule.objects.filter(role=self.role).first()
        commission_amount = 0
        if commission_rule and amount >= commission_rule.min_amount:
            commission_amount = commission_rule.calculate_commission(amount)

        total_amount = amount + commission_amount
        if total_amount > self.balance:
            raise ValueError("Insufficient balance for amount + commission")

        if commission_amount > 0:
            commission_ref_id = f"{reference_id}_commission" if reference_id else None
            if not commission_ref_id or not WalletTransaction.objects.filter(reference_id=commission_ref_id, wallet=self).exists():
                WalletTransaction.create_transaction(
                    wallet=self,
                    type=WalletTransaction.TransactionType.COMMISSION,
                    amount=commission_amount,
                    related_wallet=settings.SITE_WALLET,
                    description=f"Commission for withdrawal",
                    reference_id=commission_ref_id
                )

        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.WITHDRAW,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def freeze(self, amount: Decimal, description="", reference_id=None):
        if reference_id and WalletTransaction.objects.filter(reference_id=reference_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=reference_id, wallet=self)
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.FREEZE,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def release(self, amount: Decimal, description="", reference_id=None):
        if reference_id and WalletTransaction.objects.filter(reference_id=reference_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=reference_id, wallet=self)
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.RELEASE,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def transfer_to(self, recipient_wallet, amount: Decimal, description="", reference_id=None,
                    site_wallet=None, commission_percent=0):
        if reference_id and WalletTransaction.objects.filter(reference_id=reference_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=reference_id, wallet=self)

        if commission_percent and site_wallet:
            commission_amount = (Decimal(amount) * Decimal(commission_percent) / 100).quantize(Decimal('1.'), rounding=ROUND_DOWN)
            total_amount = amount + commission_amount
            if total_amount > self.balance:
                raise ValueError("Insufficient balance for transfer + commission")

            commission_ref_id = f"{reference_id}_commission" if reference_id else None
            if not commission_ref_id or not WalletTransaction.objects.filter(reference_id=commission_ref_id, wallet=self).exists():
                WalletTransaction.create_transaction(
                    wallet=self,
                    type=WalletTransaction.TransactionType.COMMISSION,
                    amount=commission_amount,
                    related_wallet=site_wallet,
                    description="Commission for transfer",
                    reference_id=commission_ref_id
                )
            amount_to_transfer = amount
        else:
            amount_to_transfer = amount

        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.TRANSFER,
            amount=amount_to_transfer,
            related_wallet=recipient_wallet,
            description=description,
            reference_id=reference_id
        )

    def commission(self, site_wallet, amount: Decimal, description="", reference_id=None):
        commission_ref_id = reference_id
        if commission_ref_id and WalletTransaction.objects.filter(reference_id=commission_ref_id, wallet=self).exists():
            return WalletTransaction.objects.get(reference_id=commission_ref_id, wallet=self)
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.COMMISSION,
            amount=amount,
            related_wallet=site_wallet,
            description=description,
            reference_id=commission_ref_id
        )

    def __str__(self):
        return f"{self.user} - {self.role} - {self.balance} Toman"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        db_table = 'wallets'


class SiteWallet(models.Model):
    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.CASCADE,
        related_name="site_wallet",
        verbose_name="کیف پول سایت"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Site Wallet -> {self.wallet.id}"

    class Meta:
        verbose_name = "Site Wallet"
        verbose_name_plural = "Site Wallets"
        db_table = "site_wallet"


class WalletTransaction(AmountModel):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "شارژ / واریز"
        WITHDRAW = "withdraw", "برداشت"
        FREEZE = "freeze", "مسدودسازی"
        RELEASE = "release", "آزادسازی"
        TRANSFER = "transfer", "کسر از حساب"
        COMMISSION = "commission", "کمیسیون"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=TransactionType.choices)
    related_wallet = models.ForeignKey(
        Wallet, null=True, blank=True, on_delete=models.SET_NULL, related_name="related_transactions"
    )
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user} - {self.get_type_display()} - {self.amount} Toman"

    @classmethod
    @transaction.atomic
    def create_transaction(cls, wallet, type, amount: Decimal, related_wallet=None, description="", reference_id=None):
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if type == cls.TransactionType.FREEZE:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') - amount, frozen_balance=F('frozen_balance') + amount)

        elif type == cls.TransactionType.RELEASE:
            if amount > wallet.frozen_balance:
                raise ValueError("Insufficient frozen balance")
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') + amount, frozen_balance=F('frozen_balance') - amount)

        elif type == cls.TransactionType.TRANSFER:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') - amount)
            if related_wallet:
                Wallet.objects.filter(pk=related_wallet.pk).update(balance=F('balance') + amount)

        elif type == cls.TransactionType.DEPOSIT:
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') + amount)

        elif type == cls.TransactionType.WITHDRAW:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') - amount)

        elif type == cls.TransactionType.COMMISSION:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            Wallet.objects.filter(pk=wallet.pk).update(balance=F('balance') - amount)
            if related_wallet:
                Wallet.objects.filter(pk=related_wallet.pk).update(balance=F('balance') + amount)

        wallet.refresh_from_db()
        return cls.objects.create(
            wallet=wallet,
            type=type,
            amount=amount,
            related_wallet=related_wallet,
            description=description,
            reference_id=reference_id,
        )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        db_table = 'wallet_transactions'


class CommissionRule(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان کارمزد")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="درصد کمیسیون")

    def calculate(self, amount: Decimal) -> Decimal:
        return (amount * self.percentage) / 100

    def __str__(self):
        return f"{self.title} - {self.percentage}%"


    class Meta:
        verbose_name = "Commission Rule"
        verbose_name_plural = "Commission Rules"
        db_table = "commission_rules"
