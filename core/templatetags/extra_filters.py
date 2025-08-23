from django import template
from django.utils.timezone import now
import pytz
from jalali_date import date2jalali
from jdatetime import datetime as jdatetime
import jdatetime
from datetime import datetime, date

register = template.Library()


@register.filter(name='convert_date')
def time_since_custom(value):
    if not value:
        return "نامشخص"

    current_time = now()
    diff = current_time - value
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30

    if years > 0:
        if months > 0:
            return f"{years} سال و {months} ماه پیش"
        return f"{years} سال پیش"
    elif months > 0:
        if days > 0:
            return f"{months} ماه و {days} روز پیش"
        return f"{months} ماه پیش"
    elif days > 0:
        return f"{days} روز پیش"
    else:
        return "امروز"


@register.filter(name='slice_after_space')
def truncate_words_smart(text, limit=40):
    if not text:
        return 'ثبت نشده'

    if len(text) <= limit:
        return text

    trimmed = text[:limit]
    last_space = trimmed.rfind(' ')
    if last_space != -1:
        trimmed = trimmed[:last_space]

    return trimmed + '...'


@register.filter(name='cut')
def cut(value, arg):
    return value.replace(arg, '')


@register.filter(name='show_date')
def show_jalali_date(value):
    if value:
        iran_tz = pytz.timezone('Asia/Tehran')
        localized_time = value.astimezone(iran_tz)
        return jdatetime.fromgregorian(datetime=localized_time).strftime('%Y/%m/%d - %H:%M:%S')
    return ""


JALALI_MONTHS = [
    '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
]


@register.filter(name='show_date')
def to_jalali(value):
    if not value:
        return ''
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    month_name = JALALI_MONTHS[jalali_date.month]
    return f"{jalali_date.day} {month_name} {jalali_date.year}"


@register.filter(name='show_date_slash')
def to_jalali(value):
    if not value:
        return ''
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    month_name = JALALI_MONTHS[jalali_date.month]
    return f"{jalali_date.day} / {month_name} / {jalali_date.year}"


JALALI_WEEKDAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']


@register.filter(name='show_weekday')
def show_weekday(value):
    if isinstance(value, (datetime, date)):
        jalali_date = jdatetime.date.fromgregorian(date=value)
        weekday_index = jalali_date.weekday()
        return JALALI_WEEKDAYS[weekday_index - 2]
    return ''


@register.filter(name='show_time')
def show_time(value):
    if isinstance(value, datetime):
        iran_tz = pytz.timezone('Asia/Tehran')
        value = value.astimezone(iran_tz)
        jalali = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali.strftime('%M : %H')
    return ''


@register.filter(name='show_date_with_month')
def jalali_verbose(value):
    if not value:
        return 'ثبت نشده'
    months = [
        '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    j = date2jalali(value)
    return f"{j.day} {months[j.month]} {j.year}"


@register.filter(name='three_digits')
def three_digits_sp(value: int):
    return '{:,}'.format(value)


@register.filter(name='persian_int')
def persian_int(english_int):
    devanagari_nums = ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    number = str(english_int)
    return ''.join(devanagari_nums[int(digit)] if digit.isdigit() else digit for digit in number)


@register.filter(name='three_digits_toman')
def three_digits(value):
    try:
        value = int(value)
    except ValueError:
        return value
    return '{:,}'.format(value) + ' تومان'


@register.filter(name='rounded')
def rounded(value):
    try:
        value = int(value)
        if value < 1000:
            return value
        return (value // 1000) * 1000
    except (ValueError, TypeError):
        return value


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return value


@register.simple_tag
def bask(quantity, price, x, *args, **kwargs):
    return three_digits(quantity * price + x)


@register.filter(name='sub')
def sub(x, y):
    try:
        return x - y
    except (ValueError, TypeError):
        return x


@register.filter
def format_card_number(value):
    if not value:
        return ""
    return "-".join([value[i:i + 4] for i in range(0, len(value), 4)])
