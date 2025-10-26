from urllib.parse import urlencode
from config.models import SiteSetting
from home.models import GlobalSEO


def global_seo(request):
    seo = GlobalSEO.objects.first()
    return {'seo': seo}


def canonical_url(request):
    """
    تولید URL کنونیکال تمیز و استاندارد برای تمام صفحات.
    پارامترهای تبلیغاتی و غیرضروری حذف می‌شن تا فقط URL اصلی بمونه.
    """
    base_url = request.build_absolute_uri(request.path)

    allowed_params = {'page'}

    query_params = {
        k: v for k, v in request.GET.items()
        if k in allowed_params and v
    }

    # ساخت URL نهایی
    canonical = f"{base_url}?{urlencode(query_params)}" if query_params else base_url

    return {"canonical_url": canonical}


GROUP_TRANSLATIONS = {
    "support": "پشتیبانی",
    "technical": "فنی",
    "financial": "مالی",
    "marketing": "بازاریابی",
}


def user_role(request=None, user=None):
    if user is None and request:
        user = request.user

    role = "کاربر"
    role_names = ""

    if user.is_authenticated:
        if getattr(user, "is_provider", False):
            role = "فروشنده"
        elif user.is_superuser:
            role = "مدیر"
        else:
            groups = user.groups.all()
            if groups.exists():
                role = "ک"
                translated = [GROUP_TRANSLATIONS.get(g.name, g.name) for g in groups]
                role_names = " - ".join(translated)

    if role_names:
        full_role = f"({role}. {role_names})"
    else:
        full_role = f"({role})"

    return {
        "user_role": full_role,
        "user_groups": role_names,
    }


def site_settings(request):
    try:
        site_settings = SiteSetting.objects.get(is_main=True)
    except SiteSetting.DoesNotExist:
        site_settings = None
    return {'site_settings': site_settings}
