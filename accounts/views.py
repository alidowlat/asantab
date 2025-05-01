from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from core.otp import set_user_otp, is_valid_otp
from .forms import PhoneForm, OTPForm


def phone_input_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = PhoneForm(request.POST)
            if form.is_valid():
                phone_number = form.cleaned_data['phone_number']
                user, created = User.objects.get_or_create(phone_number=phone_number)
                if created:
                    user.set_unusable_password()
                    user.save()
                set_user_otp(user)
                request.session['user_phone'] = phone_number
                return redirect('verify_page')
        else:
            form = PhoneForm()
        return render(request, 'accounts/auth.html', {'form': form})
    return render(request, 'home/index.html')


def otp_verify_view(request):
    if not request.user.is_authenticated:
        phone_number = request.session.get('user_phone')
        if not phone_number:
            return redirect('auth_page')

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return redirect('auth_page')

        if request.method == 'POST':
            form = OTPForm(request.POST)
            if form.is_valid():
                otp = form.cleaned_data['otp']
                if is_valid_otp(user, otp):
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                    login(request, user)
                    return redirect('about_us_page')
                else:
                    form.add_error('otp', 'کد وارد شده اشتباه و یا منقضی شده است.')
        else:
            form = OTPForm()

        return render(request, 'accounts/verify.html', {'form': form})
    else:
        return redirect('about_us_page')
