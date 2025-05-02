from django.db import models


class Media(models.Model):
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='media')
    file_url = models.URLField(verbose_name='آدرس فایل')
    type = models.CharField(max_length=10, choices=[('image', 'عکس'), ('video', 'ویدیو')], verbose_name='نوع مدیا')

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'
        db_table = 'media'


    def __str__(self):
        return f'{self.service.title}'
