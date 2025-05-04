import os
from django.utils.text import slugify


def get_image_upload_to(instance, filename):
    model_name = instance.__class__.__name__.lower()
    name_part = getattr(instance, 'username', None) or getattr(instance, 'slug', None) or model_name
    slug_name = slugify(name_part)
    filename = f"{slug_name}.webp"
    return os.path.join(model_name, slug_name, filename)
