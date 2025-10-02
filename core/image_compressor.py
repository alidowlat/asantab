from django.core.files.uploadedfile import InMemoryUploadedFile
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


def compress_image(uploaded_file, max_size_kb=100):
    img = Image.open(uploaded_file)
    img_format = img.format

    if img_format != 'JPEG':
        img = img.convert('RGB')
        img_format = 'JPEG'

    min_q, max_q = 20, 95
    quality = max_q
    buffer = BytesIO()

    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format=img_format, optimize=True, progressive=True, quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= min_q:
            break
        # کاهش تدریجی کیفیت
        quality -= 5

    buffer.seek(0)
    return InMemoryUploadedFile(
        buffer,
        None,
        uploaded_file.name,
        'image/jpeg',
        buffer.tell(),
        None,
    )