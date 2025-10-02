from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from core import ExpertRequiredMixin
from tickets.models import Ticket
from tickets.forms import TicketMessageForm


class AgentTicketDetailView(ExpertRequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        reply_form = TicketMessageForm()
        messages = ticket.messages.all().order_by("-created_at")
        message_list = []

        for msg in messages:
            sender_type = "agent" if getattr(msg.sender, "support_agent", False) else "user"
            message_list.append({
                "id": msg.id,
                "content": msg.message,
                "attachment": msg.attachment,
                "created_at": msg.created_at,
                "sender_type": sender_type,
                "sender_id": msg.sender.id,
                "sender_name": msg.sender.get_full_name() or msg.sender.username,
                "is_self": msg.sender.id == request.user.id
            })

        return render(request, "tickets/agent/detail.html", {
            "ticket": ticket,
            "messages": message_list,
            "reply_form": reply_form
        })

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        if not request.user.is_authenticated or not request.user.is_important_user:
            return JsonResponse({"status": "error", "message": "شما دسترسی لازم را ندارید."})

        form = TicketMessageForm(request.POST, request.FILES or None)

        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender_id = request.user.id
            message.save()

            ticket.status = 'answered'
            ticket.updated_at = timezone.now()
            ticket.save()

            return JsonResponse({
                "status": "success",
                "message": "پاسخ شما ثبت شد.",
                "redirect_url": reverse("agent_ticket_detail", args=[ticket.pk])
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "لطفاً متن پیام را وارد کنید.",
                "errors": form.errors
            })
