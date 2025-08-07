from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from accounts.models import User, Provider, ProviderPlatform


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'phone_number', 'email', 'first_name', 'last_name', 'is_active', 'is_provider', 'gender', 'birth_date')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'gender', 'is_provider')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name', 'national_id')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'otp_create_at')
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'gender', 'birth_date', 'national_id')}),
        ('دسترسی ها',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_provider', 'groups', 'user_permissions')}),
        ('تاریخچه', {'fields': ('last_login', 'date_joined', 'otp_create_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    search_fields = ['username', 'province', 'city', 'status', 'bio']
    list_filter = ['status', 'is_verified', 'province', 'city']
    list_display = ['user_id', 'username', 'status', 'is_verified', 'province', 'city', 'profile_image_display']

    def profile_image_display(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="70" height="70" style="border-radius:70%"/>',
                               obj.profile_image.url)
        return "بدون تصویر"

    profile_image_display.short_description = 'عکس پروفایل'

    fields = ['user', 'username', 'slug', 'bio', 'province', 'city', 'profile_image', 'status', 'is_verified']
    list_per_page = 20

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets += (('اطلاعات پرداخت', {
                'fields': ('iban_number', 'card_number', 'national_card_image'),
            }),)
        return fieldsets


admin.site.register(ProviderPlatform)