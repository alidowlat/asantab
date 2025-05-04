from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def compress_and_convert_to_webp(image, name_part, quality=60):
    im = Image.open(image)
    im = im.convert("RGB")

    buffer = BytesIO()
    im.save(buffer, format="WEBP", quality=quality)

    filename = f"{slugify(name_part)}.webp"
    return ContentFile(buffer.getvalue(), name=filename)
