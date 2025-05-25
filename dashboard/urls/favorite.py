from django.urls import path

from dashboard.views import FavoriteListView, dashboard_favorite_list_partial

urlpatterns = [
    path('favorite-list/', FavoriteListView.as_view(), name='favorite_list_page'),
    path('favorites/partial/', dashboard_favorite_list_partial, name='favorites_partial_list_dashboard'),
]