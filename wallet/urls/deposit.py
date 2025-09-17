from django.urls import path

from wallet.views import DepositView, deposit_verify, DepositResultView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit_view'),
    path('deposit/result/<str:ref_id>/', DepositResultView.as_view(), name='deposit_result_view'),
    path('deposit/verify/', deposit_verify, name='deposit_verify'),
]
