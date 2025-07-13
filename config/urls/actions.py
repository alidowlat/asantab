from django.urls import path
from dashboard.views import dashboard_notifications_partial
from config.views import *

urlpatterns = [
    # --- Favorites ---
    path('favorites/partial/', favorite_list_partial, name='favorite_partial_list'),
    path('favorites/count/', favorite_count, name='favorite_count'),
    path('favorites/delete/', delete_favorite, name='delete_favorite'),
    path('favorites/delete/all/', delete_all_favorites, name='delete_all_favorites'),

    # --- Visits & Search ---
    path('visits/delete/', delete_visit, name='delete_visit'),
    path('visits/delete/all/', delete_all_visits, name='delete_all_visits'),
    path('search/delete/all/', delete_all_searches, name='delete_all_searches'),

    # --- Notifications ---
    path('notifications/partial/', dashboard_notifications_partial, name='notifications_partial_list'),
    path('notif-list/partial/', notif_list_partial, name='notif_list_partial'),
    path('notifications/read/', read_notif, name='read_notif'),
    path('notifications/read/all/', read_all_notifs, name='read_all_notifs'),
    path('notifications/unread-count/', unread_notifications_count, name='unread_notifications_count'),

    # --- Orders / Cart ---
    path('order-items/partial/', cart_partial, name='cart_partial'),
    path('order-items/count/', order_items_count, name='order_items_count'),
]
