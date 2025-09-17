from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AmountModel(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="مبلغ")

    class Meta:
        abstract = True


class PSPReferenceMixin(models.Model):
    ref_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="کد مرجع PSP")
    authority = models.CharField(max_length=100, blank=True, null=True, verbose_name="شناسه درخواست (Authority)")
    tracking_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="کد پیگیری")

    class Meta:
        abstract = True
