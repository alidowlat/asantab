from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views import View
from accounts.forms import OTPForm, PhoneForm, ProviderCompleteInfoForm, ProviderLoginForm
from accounts.models import User, Provider
from accounts.views import otp_verify_view_shared, phone_input_view_shared


def provider_phone_input_view(request):
    if request.user.is_authenticated:
        if request.user.is_provider:
            return redirect('dashboard_page')
        return redirect('index_page')

    return phone_input_view_shared(
        request,
        form_class=PhoneForm,
        user_model=User,
        get_redirect_name='verify_page_provider',
        session_key='provider_phone',
        template='accounts/provider/auth.html',
        already_authenticated_template='home/index.html',
        is_provider_route=True
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
        dashboard_redirect='dashboard_page',
        session_key='provider_phone',
        template='accounts/provider/verify.html',
        fallback_redirect='auth_page_provider',
    )


def provider_complete_info_view(request):
    phone_number = request.session.get('provider_phone')
    if not request.session.get('become_provider') and not phone_number:
        return redirect('index_page')

    user = get_object_or_404(User, phone_number=phone_number)
    provider, created = Provider.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProviderCompleteInfoForm(
            request.POST,
            request.FILES,
            instance=provider,
            user=user
        )
        if form.is_valid():
            provider = form.save(commit=True)
            user.is_provider = True
            user.save(update_fields=['is_provider'])
            login(request, user)
            request.session.pop('provider_phone', None)
            return redirect('dashboard_page')
    else:
        form = ProviderCompleteInfoForm(instance=provider, user=user)

    return render(request, 'accounts/provider/complete_info.html', {'form': form})


def provider_password_input_view(request):
    if request.user.is_authenticated:
        return redirect('index_page')

    form = ProviderLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password']

        user = User.objects.filter(phone_number=phone_number).first()
        if user and user.check_password(password):
            login(request, user)
            return redirect('dashboard_page')

        form.add_error('password', 'اطلاعات وارد شده نادرست است.')

    return render(request, 'accounts/provider/password_auth.html', {'form': form})


@login_required
def become_provider_view(request):
    request.session['become_provider'] = True
    request.session['provider_phone'] = request.user.phone_number
    return redirect('complete_info_page_provider')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('auth_page_provider'))
