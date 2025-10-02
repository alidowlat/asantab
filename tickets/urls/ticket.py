from django.urls import path
from tickets.views import UserTicketListView, UserTicketDetailView, UserTicketCreateView, AgentTicketListView, agent_ticket_action, AgentTicketDetailView

urlpatterns = [
    path('list/', UserTicketListView.as_view(), name='user_ticket_list'),
    path('detail/<int:pk>', UserTicketDetailView.as_view(), name='user_ticket_detail'),
    path('create/', UserTicketCreateView.as_view(), name='user_ticket_create'),

    path('agent/list/', AgentTicketListView.as_view(), name='agent_ticket_list'),
    path('agent/detail/<int:pk>', AgentTicketDetailView.as_view(), name='agent_ticket_detail'),
    path("agent/action/<int:pk>", agent_ticket_action, name="agent_ticket_action"),
]
