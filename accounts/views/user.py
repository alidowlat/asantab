from accounts.views.shared_auth import phone_input_view_shared, otp_verify_view_shared
from django.shortcuts import redirect
from django.contrib.auth import logout
from accounts.forms import PhoneForm, OTPForm
from django.urls import reverse
from django.views import View
from accounts.models import User


def phone_input_view(request):
    return phone_input_view_shared(
        request,
        form_class=PhoneForm,
        user_model=User,
        get_redirect_name='verify_page',
        session_key='user_phone',
        template='accounts/user/auth.html',
        already_authenticated_template='home/index.html',
    )


def otp_verify_view(request):
    return otp_verify_view_shared(
        request,
        form_class=OTPForm,
        user_model=User,
        get_success_redirect='dashboard_page',
        dashboard_redirect='dashboard_page',
        session_key='user_phone',
        template='accounts/user/verify.html',
        fallback_redirect='auth_page'
    )


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('auth_page'))
