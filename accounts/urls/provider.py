from django.urls import path
from accounts.views.provider import provider_phone_input_view, provider_otp_verify_view, provider_complete_info_view, LogoutView
from accounts.services import resend_otp

urlpatterns = [
    path('', provider_phone_input_view, name='auth_page_provider'),
    path('verify/', provider_otp_verify_view, name='verify_page_provider'),
    path('complete-info/', provider_complete_info_view, name='complete_info_page_provider'),
    path('resend-otp/', resend_otp.resend_otp_view, name='resend_otp_provider'),
    path('logout/', LogoutView.as_view(), name='logout_provider'),
]
