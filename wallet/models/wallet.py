from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Wallet(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ساخته شده در")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آپدیت شده در")

    def can_withdraw(self, amount: Decimal):
        return self.balance >= amount and amount >= settings.MIN_WITHDRAW_AMOUNT

    def deposit(self, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.DEPOSIT,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def withdraw(self, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.WITHDRAW,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def freeze(self, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.FREEZE,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def release(self, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.RELEASE,
            amount=amount,
            description=description,
            reference_id=reference_id
        )

    def transfer_to(self, recipient_wallet, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.TRANSFER,
            amount=amount,
            related_wallet=recipient_wallet,
            description=description,
            reference_id=reference_id
        )

    def commission(self, site_wallet, amount: Decimal, description="", reference_id=None):
        return WalletTransaction.create_transaction(
            wallet=self,
            type=WalletTransaction.TransactionType.COMMISSION,
            amount=amount,
            related_wallet=site_wallet,
            description=description,
            reference_id=reference_id
        )

    def __str__(self):
        return f"{self.user} - {self.role} - {self.balance} Toman"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        db_table = 'wallets'


class WalletTransaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "شارژ"
        WITHDRAW = "withdraw", "برداشت"
        FREEZE = "freeze", "مسدودسازی"
        RELEASE = "release", "آزادسازی"
        TRANSFER = "transfer", "انتقال"
        COMMISSION = "commission", "کمیسیون"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
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
            wallet.balance -= amount
            wallet.frozen_balance += amount

        elif type == cls.TransactionType.RELEASE:
            if amount > wallet.frozen_balance:
                raise ValueError("Insufficient frozen balance")
            wallet.balance += amount
            wallet.frozen_balance -= amount

        elif type == cls.TransactionType.TRANSFER:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            wallet.balance -= amount
            if related_wallet:
                related_wallet.balance += amount
                related_wallet.save()

        elif type == cls.TransactionType.DEPOSIT:
            wallet.balance += amount

        elif type == cls.TransactionType.WITHDRAW:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            wallet.balance -= amount

        elif type == cls.TransactionType.COMMISSION:
            if amount > wallet.balance:
                raise ValueError("Insufficient balance")
            wallet.balance -= amount
            if related_wallet:
                related_wallet.balance += amount
                related_wallet.save()

        wallet.save()

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