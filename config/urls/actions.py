from django.urls import path

from config.views import favorite_list_partial, delete_favorite, delete_all_favorites

urlpatterns = [
    path('favorites/partial/', favorite_list_partial, name='favorite_partial_list'),
    path('favorites/delete/', delete_favorite, name='delete_favorite'),
    path('favorites/delete/all/', delete_all_favorites, name='delete_all_favorites'),
]
#