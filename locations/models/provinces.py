from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='نام استان')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'
        db_table = 'provinces'
