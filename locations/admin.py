from django.contrib import admin

from locations import models

admin.site.register(models.City)
admin.site.register(models.Province)
