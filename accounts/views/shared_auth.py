from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from accounts.models import Provider
from core import is_valid_otp, set_user_otp, send_otp
from core.cache import delete_inactive_users
from notifications.services import notify_user


def phone_input_view_shared(
        request,
        form_class,
        user_model,
        get_redirect_name,
        session_key=f"user_phone",
        template='accounts/user/auth.html',
        already_authenticated_template='home/index.html',
        is_provider_route=False
):
    delete_inactive_users(exp_in_min=15)

    if request.user.is_authenticated:
        return render(request, already_authenticated_template)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user, created = user_model.objects.get_or_create(phone_number=phone_number)

            if user.is_provider and not is_provider_route:
                request.session['redirect_to_provider_auth'] = phone_number
                return redirect('auth_page_provider')

            if created:
                user.set_unusable_password()
                user.save()

            otp = set_user_otp(user)
            user.refresh_from_db()
            send_otp(user.phone_number, otp)
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
                is_first_verification = not user.is_verified
                if is_first_verification:
                    notify_user(
                        user=user,
                        title="تکمیل حساب کاربری",
                        message="خوش آمدید! لطفا نسبت به تکمیل حساب کاربری خود اقدام کنید.",
                        type_key="complete_profile",
                        link=reverse('account_info_page')
                    )

                user.is_verified = True
                user.save(update_fields=['is_verified'])
                login(request, user)

                if user.is_important_user and user.has_usable_password():
                    request.session['two_step_user_id'] = user.id
                    return redirect('password_verify_page')
                if user.is_provider:
                    provider = get_object_or_404(Provider, user=user)
                    if provider.has_completed_required_fields():
                        return redirect(dashboard_redirect)
                return redirect(get_success_redirect)
            else:
                form.add_error('otp', 'کد وارد شده اشتباه و یا منقضی شده است.')
    else:
        form = form_class()

    return render(request, template, {'form': form})


def password_verify_view_shared(
        request,
        form_class,
        user_model,
        get_success_redirect,
        template='accounts/user/password_verify.html',
        fallback_redirect='auth_page'
):
    user_id = request.session.get('two_step_user_id')
    if not user_id:
        return redirect(fallback_redirect)

    user = get_object_or_404(user_model, id=user_id)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if user.check_password(password):
                login(request, user)
                del request.session['two_step_user_id']
                return redirect(get_success_redirect)
            else:
                form.add_error('password', 'رمز عبور اشتباه است.')
    else:
        form = form_class()

    return render(request, template, {'form': form})
