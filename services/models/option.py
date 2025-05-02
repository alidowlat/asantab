from django.db import models


class Option(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='options', verbose_name='خدمت')
    title = models.CharField(max_length=50, verbose_name='عنوان')
    unit_price = models.PositiveIntegerField(verbose_name='قیمت هر عدد')
    unit_description = models.CharField(max_length=80, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        db_table = 'options'

    def __str__(self):
        return f'{self.title} ({self.unit_price} تومان / {self.unit_description})'
