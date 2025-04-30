from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'phone_number', 'email', 'first_name', 'last_name', 'is_active', 'is_provider', 'gender', 'birth_date'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'gender', 'is_provider')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name', 'national_id')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'otp_create_time')
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'gender', 'birth_date', 'national_id')}),
        ('دسترسی ها',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_provider', 'groups', 'user_permissions')}),
        ('تاریخچه', {'fields': ('last_login', 'date_joined', 'otp_create_time')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2'),
        }),
    )
