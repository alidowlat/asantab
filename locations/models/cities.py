from django.db import models
from .provinces import Province


class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name='نام استان')
    name_fa = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='نام شهر به فارسی')
    name_en = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='نام شهر به انگلیسی')

    def __str__(self):
        if self.name_en:
            return f'{self.name_fa} - {self.name_en} ({self.province.name_fa})'
        return f'{self.name_fa} ({self.province.name_fa})'

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        db_table = 'cities'



# INSERT INTO `cities` (id, province_id, name_en) VALUES ('1', '1', 'Azarshahr');
