from django.contrib.auth import login
from django.shortcuts import redirect, render
from accounts.models import Provider
from core import is_valid_otp, set_user_otp


def phone_input_view_shared(
    request,
    form_class,
    user_model,
    get_redirect_name,
    session_key='user_phone',
    template='accounts/user/auth.html',
    already_authenticated_template='home/index.html'
):
    if request.user.is_authenticated:
        return render(request, already_authenticated_template)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user, _ = user_model.objects.get_or_create(phone_number=phone_number)
            user.set_unusable_password()
            user.save()
            otp = set_user_otp(user)
            # send_otp(user, otp)
            request.session[session_key] = phone_number
            return redirect(get_redirect_name)
    else:
        form = form_class()

    return render(request, template, {'form': form})


def otp_verify_view_shared(
    request,
    form_class,
    user_model,
    get_success_redirect,
    dashboard_redirect,
    session_key='user_phone',
    template='accounts/user/verify.html',
    fallback_redirect='auth_page'
):
    if request.user.is_authenticated:
        return redirect(get_success_redirect)

    phone_number = request.session.get(session_key)
    if not phone_number:
        return redirect(fallback_redirect)

    user = user_model.objects.filter(phone_number=phone_number).first()
    if not user:
        return redirect(fallback_redirect)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if is_valid_otp(user, otp):
                user.is_verified = True
                user.save(update_fields=['is_verified'])
                login(request, user)
                provider = Provider.objects.get(user=user)
                if provider and provider.has_completed_required_fields():
                    return redirect(dashboard_redirect)
                return redirect(get_success_redirect)
            else:
                form.add_error('otp', 'کد وارد شده اشتباه و یا منقضی شده است.')
    else:
        form = form_class()

    return render(request, template, {'form': form})