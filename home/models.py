from django.db import models


class MediaItem(models.Model):
    SECTION_CHOICES = [
        ('upper_banner', 'بنر بالای صفحه'),
        ('home_gif', 'گیف صفحه اصلی'),
        ('body_banner', 'بنر وسط صفحه'),
        ('header_link', 'لینک های هدر'),

        ('platform', 'پلتفرم ها'),
        ('category', 'دسته‌بندی‌ها'),

        ('payment', 'درگاه پرداخت'),
        ('other', 'سایر (هدر)'),
    ]

    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        verbose_name='بخش مربوطه'
    )
    title = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name='عنوان'
    )
    image_desktop = models.ImageField(
        'عکس دسکتاپ',
        upload_to='media_items/',
        null=True, blank=True,
        help_text=(
            'ابعاد پیشنهادی بسته به بخش مربوطه:\n'
            '• بنر صفحه اصلی: ۲۸۸۰×۶۰۰ پیکسل\n'
            '• گیف صفحه اصلی: ۲۸۰۰×۱۰۰ پیکسل\n'
            '• پلتفرم ها و دسته‌بندی‌ها: دلخواه'
        )
    )
    image_mobile = models.ImageField(
        'عکس موبایل',
        upload_to='media_items/',
        null=True, blank=True,
        help_text=(
            'ابعاد پیشنهادی بسته به بخش مربوطه:\n'
            '• بنر صفحه اصلی: ۲۸۸۰×۶۰۰ پیکسل\n'
            '• گیف صفحه اصلی: ۲۸۰۰×۱۰۰ پیکسل\n'
            '• پلتفرم ها و دسته‌بندی‌ها: دلخواه'
        )
    )
    link = models.URLField(
        blank=True, null=True,
        verbose_name='لینک ارجاعی'
    )
    payment_tag = models.TextField(blank=True, null=True, verbose_name='کد HTML درگاه پرداخت',
                                   help_text='تگ کامل <a> ارائه‌شده توسط درگاه پرداخت را اینجا قرار دهید.')
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال باشد؟'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        verbose_name = 'Media Item'
        verbose_name_plural = 'Media Items'
        ordering = ['order', '-created_at']
        db_table = 'media_item'

    def __str__(self):
        return self.title or f"{self.get_section_display()} #{self.id}"

    def save(self, *args, **kwargs):
        if self.section == 'home_gif' and self.is_active:
            MediaItem.objects.filter(
                section='home_gif', is_active=True
            ).exclude(id=self.id).update(is_active=False)

        super().save(*args, **kwargs)


class GlobalSEO(models.Model):
    site_title = models.CharField(max_length=255, default="Asan Tab | آسان تب")
    meta_description = models.TextField(default="پلتفرم رزرو و ارائه خدمات آنلاین آسان تب")
    meta_keywords = models.CharField(max_length=255, default="آسان تب, خدمات, رزرو, تبلیغات ارزان")
    og_title = models.CharField(max_length=255, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)
    robots_txt = models.TextField(blank=True, null=True)
    canonical_base = models.URLField(default="https://asantab.com")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global SEO Settings"

    class Meta:
        verbose_name = 'Global SEO'
        verbose_name_plural = 'Global SEO Settings'
        db_table = 'global_seo'