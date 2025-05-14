from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=35, verbose_name='عنوان')
    logo_1 = models.ImageField(upload_to='site_setting/logo_1', verbose_name='لوگو ۱')
    logo_2 = models.ImageField(upload_to='site_setting/logo_2', verbose_name='لوگو ۲')
    transparent_logo = models.ImageField(upload_to='site_setting/transparent_logo', verbose_name='لوگو شفاف')
    footer_text = models.TextField(null=True, blank=True, verbose_name="متن فوتر")
    contact_email = models.EmailField(null=True, blank=True, verbose_name="ایمیل وب سایت")
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name="شماره تماس وب سایت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین آپدیت")
    is_main = models.BooleanField(default=False, unique=True, verbose_name='تنظیمات اصلی؟')

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         old = Service.objects.get(pk=self.pk)
    #         if old.image and old.image != self.image:
    #             if old.image:
    #                 try:
    #                     default_storage.delete(old.image.name)
    #                 except Exception as e:
    #                     print(f"Error deleting old image: {e}")
    #
    #     super().save(*args, **kwargs)

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


class SocialLink(models.Model):
    site_setting = models.ForeignKey('config.SiteSetting', on_delete=models.CASCADE, verbose_name="تنظیمات")
    title = models.CharField(max_length=25, verbose_name="عنوان")
    url = models.URLField(max_length=75, verbose_name="آدرس")

    def __str__(self):
        return f'{self.site_setting} - {self.title}'

    class Meta:
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
        db_table = 'social_links'
