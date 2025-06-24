from django.db import models


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications', verbose_name='کاربر')
    title = models.CharField(max_length=175, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    link = models.URLField(null=True, blank=True, verbose_name='لینک اکشن')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده؟')
    created_at = models.DateTimeField(auto_now_add=True)
    notif_type = models.ForeignKey('notifications.NotificationType', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='نوع اعلان')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        db_table = 'notifications'

    def __str__(self):
        return f'{self.user} - {self.title}'
