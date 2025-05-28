from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from accounts.managers import UserManager

phone_regex = RegexValidator(regex=r'^09\d{9}$', message="لطفا شماره موبایل خود را به درستی وارد کنید.")
otp_regex = RegexValidator(regex=r'^\d{6}$', message='کد تایید باید دقیقا ۶ رقم عددی باشد.')
national_id_regex = RegexValidator(regex=r'^\d{10}$', message='کد ملی باید ۱۰ رقم باشد.')

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
