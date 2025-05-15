from django.db import models
from core.media_path import get_image_upload_to


class Category(models.Model):
    platform = models.ForeignKey('services.Platform', on_delete=models.SET_NULL, null=True, verbose_name='پلتفرم')
    title = models.CharField(max_length=50, verbose_name='عنوان')
    title_en = models.CharField(max_length=50, verbose_name='عنوان انگلیسی')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=50, unique=True)
    image = models.ImageField(upload_to=get_image_upload_to, null=True, blank=True, verbose_name='تصویر')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'

    def __str__(self):
        return f'{self.title}'
