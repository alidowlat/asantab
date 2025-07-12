from django.urls import path
from dashboard.views import OrderListView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_page'),
]
