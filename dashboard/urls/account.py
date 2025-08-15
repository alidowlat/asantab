from django.urls import path

from dashboard.views import AccountView, UpdateEmailView, UpdateNameView, UpdatePhoneView, UpdateNationalIDView, UpdateGenderView, \
    UpdateBirthdateView, UpdateUsernameView, UpdateBioView, UpdateLocationView, UpdateIbanView, UpdateCardNumberView, \
    UpdateProfileImageView, UpdatePasswordView, UpdatePlatformUrlsView

urlpatterns = [
    path('info/', AccountView.as_view(), name='account_info_page'),
    path('update-email/', UpdateEmailView.as_view(), name='update_email'),
    path('update-name/', UpdateNameView.as_view(), name='update_name'),
    path('update-phone/', UpdatePhoneView.as_view(), name='update_phone'),
    path('update-national-id/', UpdateNationalIDView.as_view(), name='update_national_id'),
    path('update-gender/', UpdateGenderView.as_view(), name='update_gender'),
    path('update-birthdate/', UpdateBirthdateView.as_view(), name='update_birthdate'),
    path('update-username/', UpdateUsernameView.as_view(), name='update_username'),
    path('update-bio/', UpdateBioView.as_view(), name='update_bio'),
    path('update-location/', UpdateLocationView.as_view(), name='update_location'),
    path('update-iban/', UpdateIbanView.as_view(), name='update_iban'),
    path('update-card-number/', UpdateCardNumberView.as_view(), name='update_card_number'),
    path('update-profile-image/', UpdateProfileImageView.as_view(), name='update_profile_image'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),
    path('update-platformurls/', UpdatePlatformUrlsView.as_view(), name='update_platformurls'),
]
