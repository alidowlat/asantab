from django.urls import path
from dashboard.views import OrderListView, OrderDetailView, OrderContentCreateView, ProviderOrderListView, ProviderOrderDetailView, \
    vendor_order_action, OrderContentDetailView, ProviderOrderContentDetailView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_page'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order-item/<int:item_id>/content/add/', OrderContentCreateView.as_view(), name='order_item_content_add'),
    path('order-item/<int:item_id>/content/view/', OrderContentDetailView.as_view(), name='order_item_content_view'),
    path('order-item/<int:item_id>/provider/content/view/', ProviderOrderContentDetailView.as_view(), name='provider_order_item_content_view'),
    path('received-orders/', ProviderOrderListView.as_view(), name='received_orders_page'),
    path('received-orders/<int:pk>/', ProviderOrderDetailView.as_view(), name='received_order_detail'),
    path("received-orders/<int:pk>/<str:action>/", vendor_order_action, name="vendor_order_action"),
]
