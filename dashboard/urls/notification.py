from django.urls import path

from dashboard.views import NotificationsView, dashboard_notifications_partial

urlpatterns = [
    path('notifications/', NotificationsView.as_view(), name='notifications_page'),
    path('notifications/partial/', dashboard_notifications_partial, name='notifications_partial_dashboard'),
]