from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponseForbidden

User = get_user_model()


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    from accounts.models import Provider

    providers = Provider.objects.select_related("user").all()

    used_ids = set(providers.values_list("user_id", flat=True))

    normal_users = (
        User.objects.exclude(id__in=used_ids)
        .order_by("-date_joined")
    )

    context = {
        "providers": providers,
        "users": normal_users,
    }
    return render(request, "dashboard/users/main.html", context)


@login_required
@user_passes_test(is_admin)
def impersonate_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    # جلوگیری از impersonate شدن خود مدیر
    if target_user.is_superuser:
        return HttpResponseForbidden("امکان ورود به حساب مدیر دیگر وجود ندارد.")

    # ذخیره یوزر اصلی توی سشن
    if not request.session.get("original_user_id"):
        request.session["original_user_id"] = request.user.id

    login(request, target_user)
    request.session["is_impersonating"] = True
    return redirect("/")  # مثلا صفحه اصلی سایت


@login_required
def stop_impersonate_view(request):
    original_id = request.session.get("original_user_id")
    if not original_id:
        return redirect("/")  # اگر چیزی ذخیره نشده بود

    original_user = get_object_or_404(User, id=original_id)

    # فقط اگه واقعا مدیر باشه اجازه ورود بده
    if not original_user.is_superuser:
        return HttpResponseForbidden("دسترسی غیرمجاز.")

    login(request, original_user)
    request.session.pop("original_user_id", None)
    request.session.pop("is_impersonating", None)

    return redirect("/admin-dashboard/")  # بازگشت به داشبورد مدیر
