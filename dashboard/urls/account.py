from django.urls import path

from dashboard.views import AccountView, UpdateEmailView, UpdateNameView, UpdatePhoneView, UpdateNationalIDView, UpdateGenderView, \
    UpdateBirthdateView, UpdateUsernameView

urlpatterns = [
    path('info/', AccountView.as_view(), name='account_info_page'),
    path('update-email/', UpdateEmailView.as_view(), name='update_email'),
    path('update-name/', UpdateNameView.as_view(), name='update_name'),
    path('update-phone/', UpdatePhoneView.as_view(), name='update_phone'),
    path('update-national-id/', UpdateNationalIDView.as_view(), name='update_national_id'),
    path('update-gender/', UpdateGenderView.as_view(), name='update_gender'),
    path('update-birthdate/', UpdateBirthdateView.as_view(), name='update_birthdate'),
    path('update-username/', UpdateUsernameView.as_view(), name='update_username'),
]
