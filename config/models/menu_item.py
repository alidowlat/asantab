from django.db import models


class MainCategory(models.Model):
    title = models.CharField(max_length=35, verbose_name="عنوان")
    url = models.CharField(max_length=255, verbose_name="آدرس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['order']
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"
        db_table = 'main_categories'

    def __str__(self):
        return self.title


class CategoryItem(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='category_items', verbose_name="دسته اصلی")
    title = models.CharField(max_length=100, verbose_name="عنوان")
    url = models.CharField(max_length=255, verbose_name="آدرس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        unique_together = ('main_category', 'title')
        ordering = ['order']
        verbose_name = "Category Item"
        verbose_name_plural = "Category Items"
        db_table = 'category_items'

    def __str__(self):
        return f"{self.main_category.title} --> {self.title}"
