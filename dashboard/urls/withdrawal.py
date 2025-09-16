from django.urls import path

from dashboard.views import WithdrawalRequestListView, WithdrawalRequestDetailView, withdrawal_action

urlpatterns = [
    path('withdrawals/', WithdrawalRequestListView.as_view(), name='admin_withdrawal_list'),
    path('withdrawals/<int:pk>/', WithdrawalRequestDetailView.as_view(), name='admin_withdrawals_detail'),
    path("withdrawals/<int:pk>/<str:action>/", withdrawal_action, name="admin_withdrawal_action"),

]
