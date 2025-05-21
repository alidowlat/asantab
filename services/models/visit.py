from django.db import models


class Visit(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='visits', verbose_name='خدمت')
    ip = models.CharField(max_length=64, verbose_name='IP')
    user = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.CASCADE, verbose_name='کاربر')
    user_agent = models.TextField(null=True, blank=True, verbose_name='مرورگر / دستگاه')
    referer = models.URLField(null=True, blank=True, verbose_name='صفحه ارجاع‌دهنده')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.service.title} / {self.ip}'

    class Meta:
        verbose_name = "Visit"
        verbose_name_plural = "Visits"
        db_table = 'service_visits'
