from django.urls import path
from dashboard.views import user_list_view, role_list, impersonate_view, stop_impersonate_view, provider_list_view

urlpatterns = [
    path('roles/', role_list, name='role_list'),
    path('roles/users/', user_list_view, name='user_list_manager'),
    path('roles/providers/', provider_list_view, name='provider_list_manager'),
    path('impersonate/<int:user_id>/', impersonate_view, name='impersonate_user'),
    path('stop-impersonate/', stop_impersonate_view, name='stop_impersonate'),
]
