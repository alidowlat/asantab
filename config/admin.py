from django.contrib import admin

from config.models import SiteSetting, CategoryItem, MainCategory, SocialLink

admin.site.register(SiteSetting)
admin.site.register(MainCategory)
admin.site.register(CategoryItem)
admin.site.register(SocialLink)
