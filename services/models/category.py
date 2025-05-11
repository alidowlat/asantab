from django.db import models
from django.utils.text import slugify

from core.media_path import get_image_upload_to


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    title_en = models.CharField(max_length=50, verbose_name='عنوان')
    url_title = models.CharField(max_length=50, verbose_name='عنوان در URL')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=50, unique=True)
    image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True, verbose_name='تصویر')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='والد'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.url_title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'

    def __str__(self):
        return f'{self.title}'
