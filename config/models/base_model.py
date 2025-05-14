from django.db import models


class BaseCategory(models.Model):
    title = models.CharField(max_length=35, verbose_name="عنوان")
    url = models.CharField(max_length=75, null=True, blank=True, verbose_name="آدرس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return self.title