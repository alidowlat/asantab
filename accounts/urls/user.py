from django.urls import path

from accounts.views import password_verify_view
from accounts.views.user import phone_input_view, otp_verify_view, LogoutView
from accounts.services import resend_otp

urlpatterns = [
    path('', phone_input_view, name='auth_page'),
    path('verify/', otp_verify_view, name='verify_page'),
    path('password-verify/', password_verify_view, name='password_verify_page'),
    path('resend-otp/', resend_otp.resend_otp_view, name='resend_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
