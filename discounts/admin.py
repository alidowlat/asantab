from django.contrib import admin
from discounts.models import DiscountCode, DiscountCodeUser


admin.site.register(DiscountCode)
admin.site.register(DiscountCodeUser)
