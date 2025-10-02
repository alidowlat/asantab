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
