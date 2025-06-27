from django.db import models


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, verbose_name='خدمت')
    option = models.ForeignKey('services.Option', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آپشن انتخابی')
    count = models.PositiveIntegerField(verbose_name='تعداد')
    final_price = models.PositiveIntegerField(verbose_name='قیمت نهایی')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        db_table = 'order_items'
