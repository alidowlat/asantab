from django.urls import path

from wallet.views import WalletView

urlpatterns = [
    path('', WalletView.as_view(), name="my_wallet"),
]
