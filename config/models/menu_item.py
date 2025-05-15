from django.db import models
from config.models import BaseCategory



class MainCategory(BaseCategory):
    platform = models.ForeignKey('services.Platform', on_delete=models.CASCADE, related_name='main_categories', verbose_name='پلتفرم')

    class Meta:
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"
        db_table = 'main_categories'


class CategoryItem(BaseCategory):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='category_items', verbose_name="دسته اصلی")

    class Meta:
        unique_together = ('main_category', 'title')
        verbose_name = "Category Item"
        verbose_name_plural = "Category Items"
        db_table = 'category_items'

    def __str__(self):
        return f"{self.main_category.title} --> {self.title}"
