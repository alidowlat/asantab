from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from tickets.models import Ticket


class UserTicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/user/main.html"
    context_object_name = "tickets"
    paginate_by = 10

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by("-updated_at")
