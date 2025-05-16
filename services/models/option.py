from config.models import BaseOption

from django.db import models


class Option(BaseOption):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='options', verbose_name='خدمت')

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        db_table = 'options'

    def __str__(self):
        return f'{self.title} - ({self.unit_price})'


class OptionItem(BaseOption):
    option = models.ForeignKey('Option', on_delete=models.CASCADE, related_name='items', verbose_name='خدمت')

    class Meta:
        verbose_name = 'Option Item'
        verbose_name_plural = 'Option Items'
        db_table = 'option_items'

    def __str__(self):
        return f'{self.option} ({self.unit_price} تومان / {self.title})'
