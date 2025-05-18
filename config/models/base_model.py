from django.db import models

STATUS_CHOICES = [
    ('pending', 'در انتظار تایید'),
    ('approved', 'تایید شده'),
    ('rejected', 'رد شده'),
]


class BaseCategory(models.Model):
    title = models.CharField(max_length=45, verbose_name="عنوان")
    url = models.CharField(max_length=45, null=True, blank=True, verbose_name="آدرس")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return self.title


class BaseOption(models.Model):
    title = models.CharField(max_length=50, verbose_name='عنوان')
    unit_price = models.PositiveIntegerField(verbose_name='قیمت هر عدد')
    is_active = models.BooleanField(default=True, verbose_name='فعال است؟')

    class Meta:
        abstract = True


class BaseReview(models.Model):
    user = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.CASCADE, verbose_name='کاربر')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE, verbose_name='پاسخ')
    title = models.CharField(max_length=75, null=True, blank=True, verbose_name='عنوان', )
    text = models.TextField(max_length=450, verbose_name='متن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')

    RECOMMENDATION_CHOICES = [
        ('good', 'میکنم'),
        ('bad', 'نمیکنم'),
    ]
    recommendation = models.CharField(max_length=7, null=True, blank=True, choices=RECOMMENDATION_CHOICES,
                                      verbose_name='پیشنهاد کاربر')

    class Meta:
        abstract = True
        ordering = ['-create_date']

    def __str__(self):
        return f"{self.user} - {self.text[:20]}"


class BaseReviewReaction(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='کاربر')
    reaction = models.CharField(max_length=7, choices=[('like', 'پسندیدم'), ('dislike', 'نپسندیدم')], verbose_name='ری اکشن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        abstract = True
