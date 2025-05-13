from django.contrib import admin

from config.models import SiteSetting, CategoryItem, MainCategory

admin.site.register(SiteSetting)
admin.site.register(MainCategory)
admin.site.register(CategoryItem)
