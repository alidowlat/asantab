from services.views import toggle_reaction_service, toggle_favorite_service, ServiceDetailView, add_service_review, ProviderDetailView
from orders.views import add_service_to_cart
from django.urls import path

urlpatterns = [
    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
    path('providers/<slug>', ProviderDetailView.as_view(), name='provider_detail_page'),
    path('add-to-cart', add_service_to_cart, name='add_service_to_cart'),
    path('add-review', add_service_review, name='add_service_review'),
    path('toggle-reaction', toggle_reaction_service, name='toggle_reaction_service'),
    path('toggle-favorite', toggle_favorite_service, name='toggle_favorite_service'),
]
