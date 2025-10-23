from django.http import JsonResponse
from django.shortcuts import render

from config.models import SiteSetting
from tickets.forms import ContactUsForm


def contact_us(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.user = request.user
            contact.save()
            return JsonResponse({
                "success": True,
                "message": "پیام شما با موفقیت ارسال شد!",
                "redirect_url": "/"
            })
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})
    else:
        form = ContactUsForm()

    context = {
        "form": form,
        'site_settings': SiteSetting.objects.get(is_main=True),
    }
    return render(request, "tickets/contact_us.html", context)
