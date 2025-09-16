from django.urls import path

from wallet.views import WithdrawView, WithdrawListView

urlpatterns = [
    path('withdraw/', WithdrawView.as_view(), name='withdraw_view'),
    path('withdraw/history/', WithdrawListView.as_view(), name='withdrawal_history'),
]
