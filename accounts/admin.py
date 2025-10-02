from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from accounts.models import User, Provider, BankAccount, Bank


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
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_provider', 'is_verified', 'groups', 'user_permissions')}),
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

    fields = ['user', 'username', 'slug', 'bio', 'province', 'city', 'profile_image', 'national_card_image', 'status', 'is_verified']
    list_per_page = 20


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank', 'sheba_number', 'card_number', 'created_at', 'status')
    list_filter = ['created_at']
    search_fields = ('user__phone_number', 'sheba_number', 'card_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('bank', 'user', 'sheba_number', 'card_number')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'status')
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.card_number and len(obj.card_number) >= 6:
            prefix = obj.card_number[:6]
            try:
                obj.bank = Bank.objects.get(prefix=prefix)
            except Bank.DoesNotExist:
                obj.bank = None

        super().save_model(request, obj, form, change)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "logo_preview")
    search_fields = ("name", "prefix")
    list_filter = ("name",)
    ordering = ("name",)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" style="border-radius:8px;" />', obj.logo.url)
        return "—"

    logo_preview.short_description = "لوگو"
