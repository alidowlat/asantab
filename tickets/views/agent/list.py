from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from core import ExpertRequiredMixin, expert_required
from tickets.models import Ticket


class AgentTicketListView(ExpertRequiredMixin, LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/agent/main.html"
    context_object_name = "agent_tickets"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(
            status__in=["open", "assigned"]
        ).filter(
            models.Q(assigned_to__isnull=True) | models.Q(assigned_to=user)
        ).order_by("-created_at")


@login_required
@expert_required
def agent_ticket_action(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.assigned_to and ticket.assigned_to != request.user:
        return JsonResponse({"status": "error", "message": "این تیکت قبلاً به یک کارشناس دیگر اختصاص داده شده."})

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "درخواست نامعتبر است."})

    action = request.POST.get("action")
    if action == "accept":
        ticket.assigned_to = request.user
        ticket.status = "assigned"
        ticket.save()
        return JsonResponse({"status": "success", "message": "تیکت با موفقیت به شما اختصاص داده شد."})
    elif action == "reject":
        ticket.status = "closed"
        ticket.assigned_to = None
        ticket.save()
        return JsonResponse({"status": "success", "message": "تیکت رد شد و بسته شد."})
    else:
        return JsonResponse({"status": "error", "message": "عملیات نامعتبر است."})
