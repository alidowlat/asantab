from django.contrib import admin

from tickets.models import ContactUs, TicketMessage, TicketDepartment, SupportAgent, Ticket


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'created_at', 'user')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    list_per_page = 25



class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    fields = ("sender", "message", "attachment", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "department", "status", "updated_at")
    list_filter = ("status", "department", "created_at")
    search_fields = ("subject", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    inlines = [TicketMessageInline]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "sender", "short_message", "created_at")
    search_fields = ("ticket__subject", "sender__username", "message")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    def short_message(self, obj):
        return (obj.message[:50] + "...") if obj.message and len(obj.message) > 50 else obj.message
    short_message.short_description = "متن پیام"


@admin.register(TicketDepartment)
class TicketDepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(SupportAgent)
class SupportAgentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "list_departments")
    search_fields = ("user__username", "user__email", "departments__name")
    filter_horizontal = ("departments",)

    def list_departments(self, obj):
        return ", ".join([dep.name for dep in obj.departments.all()])
    list_departments.short_description = "دپارتمان‌ها"