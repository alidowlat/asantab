from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.models import User
from dashboard.forms import PhoneNumberChangeForm, PhoneNumberVerifyForm
from core.otp import send_otp, set_user_otp


@login_required
def change_phone_number(request):
    if request.method == "POST":
        form = PhoneNumberChangeForm(request.POST)
        if form.is_valid():
            new_phone_number = form.cleaned_data['phone_number']

            if new_phone_number == request.user.phone_number:
                form.add_error('phone_number', "شماره جدید نباید با شماره فعلی یکسان باشد.")
            elif User.objects.filter(phone_number=new_phone_number).exclude(pk=request.user.pk).exists():
                form.add_error('phone_number', "این شماره قبلا در وب سایت ثبت شده است.")
            else:
                otp = set_user_otp(request.user)
                send_otp(request.user, otp)

                request.session['phone_change_number'] = new_phone_number
                request.session['phone_change_otp'] = otp

                return redirect("verify_phone_number_page")

        return render(request, "dashboard/account/change_number.html", {"form": form})
    else:
        form = PhoneNumberChangeForm()
        return render(request, "dashboard/account/change_number.html", {"form": form})



@login_required
def verify_phone_change(request):
    new_phone_number = request.session.get("phone_change_number")
    otp = request.session.get("phone_change_otp")

    if not new_phone_number or not otp:
        return redirect("change_phone_number")

    if request.method == "POST":
        form = PhoneNumberVerifyForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp'] == request.session['phone_change_otp']:
                request.user.phone_number = request.session['phone_change_number']
                request.user.save()

                del request.session['phone_change_number']
                del request.session['phone_change_otp']

                return redirect("account_info_page")
            else:
                form.add_error('otp', "کد وارد شده صحیح نیست.")
    else:
        form = PhoneNumberVerifyForm()

    return render(request, "dashboard/account/verify_number.html", {"form": form})
