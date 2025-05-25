from django.urls import path

from dashboard.views import VisitListView, dashboard_visit_list_partial

urlpatterns = [
    path('recent-visits/', VisitListView.as_view(), name='visit_list_page'),
    path('visits/partial/', dashboard_visit_list_partial, name='visits_partial_list_dashboard'),
]
