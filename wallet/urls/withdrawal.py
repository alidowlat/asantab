from django.urls import path

from wallet.views import WithdrawView, WithdrawResultView, withdrawal_verify

urlpatterns = [
    path('withdraw/', WithdrawView.as_view(), name='withdraw_view'),
    path('withdraw/result/<str:ref_id>/', WithdrawResultView.as_view(), name='withdraw_result_view'),
    path('withdraw/verify/', withdrawal_verify, name='withdraw_verify'),
]
