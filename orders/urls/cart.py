from django.urls import path
from orders.views import user_cart, update_cart_data, change_cart_item_count, remove_cart_item, clear_cart_items, order_checkout, \
    cart_cleanup_view

urlpatterns = [
    path('cart', user_cart, name='user_cart_page'),
    path('checkout', order_checkout, name='order_checkout_page'),
    path('update-cart', update_cart_data, name='update_cart_data'),
    path('change-item', change_cart_item_count, name='change_cart_item_count'),
    path('remove-item', remove_cart_item, name='remove_cart_item'),
    path('clear-cart', clear_cart_items, name='clear_cart_items'),
    path('cleanup-cart', cart_cleanup_view, name='cart_cleanup_view'),
]
