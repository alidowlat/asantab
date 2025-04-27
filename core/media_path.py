import os
from django.utils.text import slugify


def get_image_upload_to(instance, filename):
    model_name = instance.__class__.__name__.lower()
    name_part = getattr(instance, 'username', None) or getattr(instance, 'slug', None) or model_name
    slug_name = slugify(name_part)
    ext = filename.split('.')[-1]
    filename = f"{slug_name}.{ext}"
    return os.path.join(model_name, slug_name, filename)
