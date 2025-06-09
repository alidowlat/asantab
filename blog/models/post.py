from django.core.files.storage import default_storage
from django.db import models
from django.urls import reverse
from core import get_image_upload_to, compress_and_convert_to_webp


class Post(models.Model):
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='posts', verbose_name='نویسنده')
    title = models.CharField(max_length=100, verbose_name='عنوان پست')
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=100, unique=True)
    image = models.ImageField(upload_to=get_image_upload_to, null=True, verbose_name='تصویر پست')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده در تاریخ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آپدیت شده در تاریخ')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    is_unique = models.BooleanField(default=False, verbose_name='ویژه است؟')
    category = models.ForeignKey('blog.Category', on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name='دسته بندی')

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk:
            old = Post.objects.get(pk=self.pk)
            if old.image and old.image != self.image:
                if old.image:
                    try:
                        default_storage.delete(old.image.name)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")

        if self.image:
            old_image_name = getattr(self, 'image', None)
            if old_image_name and old_image_name != self.image.name:
                name_part = getattr(self, 'username', None) or getattr(self, 'slug', None) or self.__class__.__name__.lower()
                self.image = compress_and_convert_to_webp(self.image, name_part, quality=75)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        db_table = 'posts'
