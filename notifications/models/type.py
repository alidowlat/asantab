from django.db import models


class NotificationType(models.Model):
    key = models.CharField(max_length=55, unique=True, verbose_name='کلید')
    title = models.CharField(max_length=85, verbose_name='عنوان نمایشی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Notification Type'
        verbose_name_plural = 'Notification Types'
        db_table = 'notification_types'