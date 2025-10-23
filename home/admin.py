from django.contrib import admin
from django.utils.html import format_html

from .models import MediaItem, GlobalSEO, InfoItem


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'link_display', 'order', 'is_active', 'created_at', 'preview_image')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'link')
    list_editable = ('order', 'is_active')
    ordering = ('order', '-created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('section', 'title', 'image_desktop', 'image_mobile', 'link', 'payment_tag', 'order', 'is_active')
        }),
        ('سایر', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def preview_image(self, obj):
        html = ''
        if obj.image_desktop:
            html += f'<img src="{obj.image_desktop.url}" style="width:60px; height:auto; border-radius:6px; margin-left:5px;" />'
        if obj.image_mobile:
            html += f'<img src="{obj.image_mobile.url}" style="width:60px; height:auto; border-radius:6px;" />'
        if not html:
            html = '—'
        return format_html(html)

    preview_image.allow_tags = True
    preview_image.short_description = 'پیش‌نمایش'

    def link_display(self, obj):
        if obj.link:
            return f'<a href="{obj.link}" target="_blank">{obj.link[:40]}...</a>' if len(
                obj.link) > 40 else f'<a href="{obj.link}" target="_blank">{obj.link}</a>'
        return '—'

    link_display.allow_tags = True
    link_display.short_description = 'لینک ارجاعی'


admin.site.register(InfoItem)
admin.site.register(GlobalSEO)