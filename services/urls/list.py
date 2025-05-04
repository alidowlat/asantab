from django.urls import path

from services.views.list import ServiceListView

urlpatterns = [
    path('', ServiceListView.as_view(), name='services_list_page'),
]
