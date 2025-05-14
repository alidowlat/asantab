from django.contrib import admin
from config.models import SiteSetting, CategoryItem, MainCategory, FooterBox, FooterLink

admin.site.register(SiteSetting)
admin.site.register(FooterBox)
admin.site.register(FooterLink)
admin.site.register(MainCategory)
admin.site.register(CategoryItem)
