from django.db import models
from .provinces import Province


class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name='نام استان')
    name = models.CharField(max_length=50, unique=True, verbose_name='نام شهر')

    def __str__(self):
        return f"{self.name} ( {self.province.name} )"

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        db_table = 'cities'
