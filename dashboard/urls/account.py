from django.urls import path

from dashboard.views import AccountView, UpdateEmailView, UpdateNameView, UpdatePhoneView, UpdateNationalIDView

urlpatterns = [
    path('info/', AccountView.as_view(), name='account_info_page'),
    path('update-email/', UpdateEmailView.as_view(), name='update_email'),
    path('update-name/', UpdateNameView.as_view(), name='update_name'),
    path('update-phone/', UpdatePhoneView.as_view(), name='update_phone'),
    path('update-national-id/', UpdateNationalIDView.as_view(), name='update_national_id'),
]
