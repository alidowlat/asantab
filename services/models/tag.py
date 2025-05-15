from django.db import models


class Tag(models.Model):
    title = models.CharField(max_length=35, verbose_name='عنوان', unique=True)
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=35, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        db_table = "tags"

    def __str__(self):
        return self.title
