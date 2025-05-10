from django.db import models
from django.db.models import Max
from django.utils.text import slugify
from core.media_path import get_image_upload_to
from core.image_compressor import compress_and_convert_to_webp

STATUS_CHOICES = [
    ('pending', 'در انتظار تایید'),
    ('approved', 'تایید شده'),
    ('rejected', 'رد شده'),
]


class Service(models.Model):
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='services', verbose_name='ارائه دهنده')
    title = models.CharField(max_length=120, verbose_name='عنوان خدمت')
    url_title = models.CharField(max_length=120, verbose_name='عنوان خدمت در URL')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=120, unique=True)
    description = models.TextField(max_length=800, verbose_name='توضیحات')
    image = models.ImageField(upload_to=get_image_upload_to, null=True, verbose_name='تصویر خدمت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده در تاریخ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آپدیت شده در تاریخ')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    is_unique = models.BooleanField(default=False, verbose_name='ویژه است؟')
    code = models.PositiveIntegerField(verbose_name='کد خدمت', unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    category = models.ForeignKey('services.Category', on_delete=models.SET_NULL, null=True, related_name='services',
                                 verbose_name='دسته بندی')
    profession = models.ForeignKey('services.Profession', on_delete=models.CASCADE, related_name='services', verbose_name='صنف')
    tags = models.ManyToManyField('services.Tag', related_name='services', verbose_name='تگ / تگ ها')
    locations = models.ManyToManyField('locations.City', related_name='services', verbose_name='شهر های قابل ارائه برای خدمات')

    # todo: get_absolute_url

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.url_title)

        if not self.code:
            last_code = Service.objects.aggregate(Max('code'))['code__max'] or 100
            self.code = last_code + 1

        try:
            this = Service.objects.get(pk=self.pk)
            if this.image and this.image != self.image:
                this.image.delete(save=False)
        except Service.DoesNotExist:
            pass

        if self.image:
            name_part = getattr(self, 'username', None) or getattr(self, 'slug', None) or self.__class__.__name__.lower()
            self.image = compress_and_convert_to_webp(self.image, name_part, quality=65)

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
        ]
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        db_table = 'services'

