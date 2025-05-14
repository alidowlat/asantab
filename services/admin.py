from django.contrib import admin

from services.models import Tag, Option, Service, Schedule, Profession, Media, Category, Reservation, Platform

admin.site.register(Category)
admin.site.register(Media)
admin.site.register(Option)
admin.site.register(Platform)
admin.site.register(Profession)
admin.site.register(Reservation)
admin.site.register(Schedule)
admin.site.register(Service)
admin.site.register(Tag)
