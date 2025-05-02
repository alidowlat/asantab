from django.db import models
from django.utils.text import slugify

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده در تاریخ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آپدیت شده در تاریخ')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    category = models.ForeignKey('services.Category', on_delete=models.SET_NULL, null=True, related_name='services',
                                 verbose_name='دسته بندی')
    profession = models.ForeignKey('services.Profession', on_delete=models.CASCADE, related_name='services', verbose_name='صنف')
    tags = models.ManyToManyField('services.Tag', related_name='services', verbose_name='تگ / تگ ها')

    # todo: get_absolute_url

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.url_title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        db_table = 'services'
