from django.urls import path

from dashboard.views import BankAccountListView, dashboard_bank_accounts_partial, BankAccountCreateView, BankAccountUpdateView, \
    delete_bank_account

urlpatterns = [
    path('bank-account/', BankAccountListView.as_view(), name='bank_accounts_view'),
    path('bank-account/partial/', dashboard_bank_accounts_partial, name='bank_partial_list_dashboard'),
    path('bank-account/create/', BankAccountCreateView.as_view(), name='bank_account_create_view'),
    path('bank-account/edit/<int:pk>/', BankAccountUpdateView.as_view(), name='bank_account_edit_view'),
    path('bank-account/delete/', delete_bank_account, name='delete_bank_account'),
]
