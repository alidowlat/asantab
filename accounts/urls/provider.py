from django.urls import path
from accounts.views.provider import *
from accounts.services import resend_otp

urlpatterns = [
    path('', provider_phone_input_view, name='auth_page_provider'),
    path('with-password/', provider_password_input_view, name='auth_page_provider_password'),
    path('verify/', provider_otp_verify_view, name='verify_page_provider'),
    path('complete-info/', provider_complete_info_view, name='complete_info_page_provider'),
    path('become-provider/', become_provider_view, name='become_provider'),
    path('resend-otp/', resend_otp.resend_otp_view, name='resend_otp_provider'),
    path('logout/', LogoutView.as_view(), name='logout_provider'),
]
