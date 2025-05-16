from django.db import models


class BaseCategory(models.Model):
    title = models.CharField(max_length=45, verbose_name="عنوان")
    url = models.CharField(max_length=45, null=True, blank=True, verbose_name="آدرس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return self.title


class BaseOption(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    unit_price = models.PositiveIntegerField(verbose_name='قیمت هر عدد')
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    class Meta:
        abstract = True
