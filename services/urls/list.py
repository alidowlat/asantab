from django.urls import path

from services.views.list import ServiceListView, toggle_unique_status

urlpatterns = [
    path('', ServiceListView.as_view(), name='services_list_page'),
    path('<int:pk>/toggle-unique/', toggle_unique_status, name='toggle_unique'),
]
