from django.contrib import admin
from orders.models import OrderItem, Order, VendorOrder


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'service',
        'get_option',
        'get_schedule',
        'count',
        'final_price',
        'get_order',
        'get_vendor_order',
    )
    list_select_related = ('service', 'option', 'schedule', 'order', 'vendor_order')
    list_filter = ('service', 'option', 'schedule')
    search_fields = (
        'service__title',
        'option__title',
        'order__id',
        'vendor_order__id',
    )
    ordering = ('-id',)
    readonly_fields = ('final_price',)
    list_per_page = 30

    @admin.display(description="سفارش کاربر")
    def get_order(self, obj):
        return f"#{obj.order.id}"

    @admin.display(description="سفارش فروشنده")
    def get_vendor_order(self, obj):
        return f"#{obj.vendor_order.id}" if obj.vendor_order else "—"

    @admin.display(description="آپشن")
    def get_option(self, obj):
        return obj.option.title if obj.option else "—"

    @admin.display(description="زمان رزرو")
    def get_schedule(self, obj):
        return obj.schedule.date if obj.schedule else "—"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('service', 'option', 'schedule', 'count', 'final_price')
    can_delete = False
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tracking_code',
        'user',
        'status',
        'is_paid',
        'get_paid_at',
        'get_created_at',
    )
    list_filter = (
        'status',
        'is_paid',
    )
    search_fields = (
        'tracking_code',
        'user__phone_number',
        'user__first_name',
        'user__last_name',
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ('اطلاعات کاربر و وضعیت', {
            'fields': ('user', 'status', 'is_paid')
        }),
        ('کد و تخفیف', {
            'fields': ('tracking_code', 'discount_code')
        }),
        ('تراکنش و زمان‌ها', {
            'fields': ('wallet_transaction', 'paid_at', 'created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        return request.user.is_superuser

    @admin.display(description="تاریخ پرداخت")
    def get_paid_at(self, obj):
        return obj.paid_at or '-'

    @admin.display(description="تاریخ ایجاد")
    def get_created_at(self, obj):
        return obj.created_at or '-'


@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'provider',
        'status',
        'total_price',
        'get_created_at',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'order__tracking_code',
        'provider__user__first_name',
        'provider__user__last_name',
        'provider__user__phone_number',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)
    fieldsets = (
        ('اطلاعات سفارش فروشنده', {
            'fields': ('order', 'provider', 'status', 'total_price')
        }),
        ('اطلاعات تکمیلی', {
            'fields': ('rejection_reason', 'created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        return request.user.is_superuser

    @admin.display(description="تاریخ ایجاد")
    def get_created_at(self, obj):
        return obj.created_at or '-'
