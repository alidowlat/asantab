from django.db import models


class Province(models.Model):
    name_fa = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='نام استان به فارسی')
    name_en = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='نام استان به انگلیسی')

    def __str__(self):
        return f'{self.name_fa}'

    class Meta:
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'
        db_table = 'provinces'
