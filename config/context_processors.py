from urllib.parse import urlencode

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


def user_role(request):
    role = "user"
    role_names = ""

    if request.user.is_authenticated:
        if getattr(request.user, "is_provider", False):
            role = "فروشنده"
        elif request.user.is_superuser:
            role = "مدیر"
        else:
            groups = request.user.groups.all()
            if groups.exists():
                role = "کارشناس"
                translated = [GROUP_TRANSLATIONS.get(g.name, g.name) for g in groups]
                role_names = " - ".join(translated)

    return {
        "user_role": role,
        "user_groups": role_names,
    }
