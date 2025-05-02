from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان', unique=True)
    url_title = models.CharField(max_length=200, verbose_name='عنوان در URL')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=200, unique=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.url_title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        db_table = "tags"

    def __str__(self):
        return self.title


    # todo: get_absolute_url