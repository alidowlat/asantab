from django.db import models


class Platform(models.Model):
    title = models.CharField(max_length=35, unique=True)
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=35, unique=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Platform'
        verbose_name_plural = 'Platforms'
        db_table = 'platforms'
