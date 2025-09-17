from django.urls import path
from dashboard.views import *

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_page'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('received-orders/', ProviderOrderListView.as_view(), name='received_orders_page'),
    path('received-orders/<int:pk>/', ProviderOrderDetailView.as_view(), name='received_order_detail'),
    path("received-orders/<int:pk>/<str:action>/", vendor_order_action, name="vendor_order_action"),
]
