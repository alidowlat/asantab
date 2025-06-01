from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404, render
from accounts.forms import OTPForm, PhoneForm, ProviderCompleteInfoForm
from accounts.models import User
from accounts.views import otp_verify_view_shared, phone_input_view_shared


def provider_phone_input_view(request):
    if request.user.is_authenticated:
        if request.user.is_provider:
            return redirect('dashboard_page')
        return redirect('about_us_page')

    return phone_input_view_shared(
        request,
        form_class=PhoneForm,
        user_model=User,
        get_redirect_name='verify_page_provider',
        session_key='provider_phone',
        template='accounts/provider/auth.html',
        already_authenticated_template='home/index.html',
    )


def provider_otp_verify_view(request):
    if request.user.is_authenticated:
        if request.user.is_provider:
            return redirect('dashboard_page')
        return redirect('complete_info_page_provider')

    return otp_verify_view_shared(
        request,
        form_class=OTPForm,
        user_model=User,
        get_success_redirect='complete_info_page_provider',
        session_key='provider_phone',
        template='accounts/provider/verify.html',
        fallback_redirect='auth_page_provider',
    )


def provider_complete_info_view(request):
    phone_number = request.session.get('provider_phone')
    if not phone_number:
        return redirect('auth_page_provider')

    user = get_object_or_404(User, phone_number=phone_number)

    if request.method == 'POST':
        form = ProviderCompleteInfoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_provider = True
            user.save()
            login(request, user)
            request.session.pop('provider_phone', None)
            return redirect('dashboard_page')
    else:
        form = ProviderCompleteInfoForm(instance=user)

    return render(request, 'accounts/provider/complete_info.html', {'form': form})
