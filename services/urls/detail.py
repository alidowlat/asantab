from services.views import toggle_reaction_service, toggle_favorite_service
from services.views.detail import ServiceDetailView, add_service_review
from django.urls import path

urlpatterns = [
    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
    path('add-review', add_service_review, name='add_service_review'),
    path('toggle-reaction', toggle_reaction_service, name='toggle_reaction_service'),
    path('toggle-favorite', toggle_favorite_service, name='toggle_favorite_service'),
]
