from django.urls import path
from dashboard.views import OrderListView, OrderDetailView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_page'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

]
