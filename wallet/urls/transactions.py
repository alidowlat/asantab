from django.urls import path

from wallet.views import RecentTransactionsView

urlpatterns = [
    path('recent-transactions/', RecentTransactionsView.as_view(), name="recent_transactions"),
]
