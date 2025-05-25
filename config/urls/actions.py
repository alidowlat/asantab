from django.urls import path

from config.views import favorite_list_partial, delete_favorite, delete_all_favorites, favorite_count, delete_visit, delete_all_visits

urlpatterns = [
    path('favorites/partial/', favorite_list_partial, name='favorite_partial_list'),
    path('favorites/count/', favorite_count, name='favorite_count'),
    path('favorites/delete/', delete_favorite, name='delete_favorite'),
    path('favorites/delete/all/', delete_all_favorites, name='delete_all_favorites'),
    path('visits/delete/', delete_visit, name='delete_visit'),
    path('visits/delete/all/', delete_all_visits, name='delete_all_visits'),
]
