from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from .user import User
from core.media_path import get_image_upload_to

STATUS_CHOICES = (
    ('pending', 'در انتظار تایید'),
    ('active', 'فعال'),
    ('rejected', 'رد شده'),
)

iban_regex = RegexValidator(regex=r'^\d{24}$', message='شماره شبا باید ۲۴ رقم باشد.')
card_regex = RegexValidator(regex=r'^\d{16}$', message='شماره کارت باید ۱۶ رقم باشد.')


class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='providers')
    username = models.CharField(max_length=60, unique=True, null=False, blank=False, verbose_name='نام کاربری')
    slug = models.SlugField(
        max_length=60,
        default="",
        null=False,
        db_index=True,
        blank=True,
        unique=True)
    bio = models.TextField(null=True, blank=True, verbose_name='بیوگرافی')
    province = models.CharField(
        max_length=100,
        # choices=PROVINCES,
        verbose_name="استان محل سکونت",
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=100,
        # choices=CITIES.get(province, []),
        verbose_name="شهر محل سکونت",
        null=True,
        blank=True
    )
    profile_image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True,
                                      verbose_name='تصویر پروفایل')
    iban_number = models.CharField(max_length=24, validators=[iban_regex], null=True, blank=True,
                                   verbose_name='شماره شبا')
    card_number = models.CharField(max_length=16, validators=[card_regex], null=True, blank=True,
                                   verbose_name='شماره کارت')
    national_card_image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True,
                                            verbose_name='تصویر کارت ملی')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده؟')

    def __str__(self):
        return self.user.get_full_name() or self.user.phone_number

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        db_table = 'providers'
