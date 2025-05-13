from django.db import models
from core.media_path import get_image_upload_to


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=35, verbose_name='عنوان')
    logo_1 = models.ImageField(upload_to=get_image_upload_to, verbose_name='لوگو ۱')
    logo_2 = models.ImageField(upload_to=get_image_upload_to, verbose_name='لوگو ۲')
    transparent_logo = models.ImageField(upload_to=get_image_upload_to, verbose_name='لوگو شفاف')
    footer_text = models.TextField(null=True, blank=True, verbose_name="متن فوتر")
    contact_email = models.EmailField(null=True, blank=True, verbose_name="ایمیل وب سایت")
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name="شماره تماس وب سایت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین آپدیت")

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = "Site Settings"
        db_table = 'site_settings'

    def __str__(self):
        return self.site_name


class FooterBox(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")

    class Meta:
        verbose_name = "Footer Box"
        verbose_name_plural = "Footer Boxes"
        db_table = 'footer_boxes'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    footer_box = models.ForeignKey('config.FooterBox', on_delete=models.CASCADE, verbose_name="باکس")
    title = models.CharField(max_length=35, verbose_name="عنوان")
    url = models.URLField(max_length=255, verbose_name="لینک")

    class Meta:
        verbose_name = "Footer Link"
        verbose_name_plural = "Footer Links"
        db_table = 'footer_links'

    def __str__(self):
        return f'{self.title} - {self.footer_box}'
