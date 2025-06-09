from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=50, unique=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'blog_categories'

    def __str__(self):
        return f'{self.title}'
