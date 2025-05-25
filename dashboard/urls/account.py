from django.urls import path

from dashboard.views.account import AccountView

urlpatterns = [
    path('info/', AccountView.as_view(), name='account_info_page'),
]