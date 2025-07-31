from django.db import models


class Profession(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=50, unique=True)
    description = models.TextField(max_length=255, blank=True, null=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = "Profession"
        verbose_name_plural = "Professions"
        db_table = 'professions'

    def __str__(self):
        return f'{self.title}'
