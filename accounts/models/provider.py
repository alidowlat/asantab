from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .user import User
from core.media_path import get_image_upload_to
from core.image_compressor import compress_and_convert_to_webp

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
    province = models.ForeignKey('locations.Province', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="استان محل سکونت")
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شهر محل سکونت")
    profile_image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True,
                                      verbose_name='تصویر پروفایل')
    national_card_image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True,
                                            verbose_name='تصویر کارت ملی')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده؟')
    is_profile_complete = models.BooleanField(default=False, verbose_name='پروفایل تکمیل شده؟')
    instagram_url = models.URLField(blank=True, null=True)
    telegram_url = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')

    def __str__(self):
        return self.user.get_full_name() or self.user.phone_number

    def get_absolute_url(self):
        return reverse('provider_detail_page', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)

        try:
            this = Provider.objects.get(pk=self.pk)
            if this.profile_image and this.profile_image != self.profile_image:
                this.profile_image.delete(save=False)
        except Provider.DoesNotExist:
            pass

        if self.profile_image:
            name_part = getattr(self, 'username', None) or getattr(self, 'slug', None) or self.__class__.__name__.lower()
            self.profile_image = compress_and_convert_to_webp(self.profile_image, name_part, quality=50)

        if self.national_card_image:
            name_part = f"national_card_{self.username}"
            self.national_card_image = compress_and_convert_to_webp(self.national_card_image, name_part)

        super().save(*args, **kwargs)

    def has_completed_required_fields(self):
        return all([
            bool(self.username),
            bool(self.province_id),
            bool(self.city_id),
        ])

    def has_completed_important_fields(self):
        return all([
            bool(self.iban_number),
            bool(self.card_number),
            bool(self.national_card_image),
        ])

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
        db_table = 'providers'

