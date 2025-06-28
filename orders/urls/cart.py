from django.urls import path
from orders.views import user_cart, update_cart_data, change_cart_item_count, remove_cart_item

urlpatterns = [
    path('cart/', user_cart, name='user_cart_page'),
    path('update-cart/', update_cart_data, name='update_cart_data'),
    path('change-order/', change_cart_item_count, name='change_cart_item_count'),
    path('remove-order/', remove_cart_item, name='remove_cart_item'),
]
