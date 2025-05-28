from django.urls import path

from dashboard.views import change_phone_number, verify_phone_change

urlpatterns = [
    path('change-number/', change_phone_number, name='change_phone_number_page'),
    path('verify-number/', verify_phone_change, name='verify_phone_number_page'),
]
