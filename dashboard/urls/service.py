from django.urls import path
from dashboard.views import ProviderServiceList, ProviderServiceCreate, ProviderServiceEdit, dashboard_services_partial, \
    delete_service, add_option, delete_option, add_schedule, delete_schedule

urlpatterns = [
    path('services/', ProviderServiceList.as_view(), name='provider_service_list'),
    path('services/create/', ProviderServiceCreate.as_view(), name='provider_service_create'),
    path('services/edit/<slug>/', ProviderServiceEdit.as_view(), name='provider_service_edit'),
    path('services/partial/', dashboard_services_partial, name='provider_services_partial_dashboard'),
    path('services/delete/', delete_service, name='delete_service'),
    path('services/option/add/', add_option, name='add_option'),
    path('services/option/delete/<int:pk>', delete_option, name='delete_option'),
    path('services/schedule/add/', add_schedule, name='add_schedule'),
    path('services/schedule/delete/<int:pk>', delete_schedule, name='delete_schedule'),
]

