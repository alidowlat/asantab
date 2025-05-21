from django.urls import path
from . import views
from .services import resend_otp

urlpatterns = [
    path('', views.phone_input_view, name='auth_page'),
    path('verify/', views.otp_verify_view, name='verify_page'),
    path('resend-otp/', resend_otp.resend_otp_view, name='resend_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
