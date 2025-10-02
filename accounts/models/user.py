from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from accounts.managers import UserManager

phone_regex = RegexValidator(regex=r'^09\d{9}$', message="لطفا شماره موبایل خود را به درستی وارد کنید.")
otp_regex = RegexValidator(regex=r'^\d{6}$', message='کد تایید باید دقیقا ۶ رقم عددی باشد.')
national_id_regex = RegexValidator(regex=r'^\d{10}$', message='کد ملی باید ۱۰ رقم باشد.')
sheba_regex = RegexValidator(regex=r'^\d{24}$', message='شماره شبا باید ۲۴ رقم باشد.')
card_regex = RegexValidator(regex=r'^\d{16}$', message='شماره کارت باید ۱۶ رقم باشد.')

STATUS_CHOICES = [
    ('pending', 'در انتظار تایید'),
    ('approved', 'تایید شده'),
    ('rejected', 'رد شده'),
]

GENDER_CHOICES = (
    ('', 'انتخاب کنید...'),
    ('M', 'مرد'),
    ('F', 'زن'),
)


class User(AbstractUser):
    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    first_name = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="نام"
    )
    last_name = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="نام خانوادگی"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        unique=True,
        max_length=11,
        blank=False,
        null=False,
        verbose_name="شماره موبایل"
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='ایمیل'
    )
    otp = models.CharField(
        max_length=5,
        validators=[otp_regex],
        null=True,
        blank=True,
        verbose_name="کد تایید"
    )
    otp_create_at = models.DateTimeField(auto_now=True)
    is_provider = models.BooleanField(
        default=False,
        verbose_name="فروشنده است؟"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name="جنسیت"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ تولد"
    )
    national_id = models.CharField(
        max_length=10,
        validators=[national_id_regex],
        unique=True,
        null=True,
        blank=True,
        verbose_name="کد ملی"
    )
    is_verified = models.BooleanField(default=False, verbose_name="تایید شده؟")

    @property
    def is_important_user(self):
        return self.groups.filter(name__in=["vip", "supports", "managers"]).exists()

    def has_completed_important_fields(self):
        return all([
            bool(self.first_name),
            bool(self.last_name),
            bool(self.email),
            bool(self.national_id),
        ])

    def get_full_name(self):
        return f"{(self.first_name or '').strip()} {(self.last_name or '').strip()}".strip()

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return full_name
        return self.email or self.phone_number or "Unknown User"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_accounts", verbose_name="کاربر")
    bank = models.ForeignKey('accounts.Bank', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="بانک")
    sheba_number = models.CharField(max_length=24, validators=[sheba_regex], unique=True, verbose_name="شماره شبا")
    card_number = models.CharField(max_length=16, validators=[card_regex], unique=True, verbose_name="شماره کارت")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def save(self, *args, **kwargs):
        if self.card_number and len(self.card_number) >= 6:
            prefix = self.card_number[:6]
            try:
                self.bank = Bank.objects.get(prefix=prefix)
            except Bank.DoesNotExist:
                self.bank = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.card_number}"

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        db_table = 'bank_accounts'


class Bank(models.Model):
    name = models.CharField(max_length=40, verbose_name='نام')
    prefix = models.CharField(max_length=6, unique=True, verbose_name='پیش شماره')
    logo = models.ImageField(upload_to="banks/", verbose_name='لوگو')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Bank'
        verbose_name_plural = 'Banks'
        db_table = 'banks'
