from services.views.detail import ServiceDetailView
from django.urls import path

urlpatterns = [
    path('<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
]
