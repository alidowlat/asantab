from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from tickets.models import Ticket
from tickets.forms import TicketMessageForm


class UserTicketDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Ticket
    template_name = "tickets/user/detail.html"
    context_object_name = "ticket"
    form_class = TicketMessageForm

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("user_ticket_detail", kwargs={"pk": self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = self.object
            message.sender = request.user
            message.save()

            self.object.status = 'assigned'
            self.object.updated_at = timezone.now()
            self.object.save()

            return JsonResponse({
                "status": "success",
                "message": "پیام شما با موفقیت ارسال شد.",
                "redirect_url": reverse("user_ticket_detail", kwargs={"pk": self.object.pk})
            })
        else:
            error_text = form.errors.get("message")
            return JsonResponse({
                "status": "error",
                "message": "پیام نمی‌تواند خالی باشد.",
                "errors": error_text
            })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages = self.object.messages.order_by("-created_at")
        message_list = []

        for msg in messages:
            sender_type = "agent" if hasattr(msg.sender, "support_agent") else "user"
            message_list.append({
                "id": msg.id,
                "content": msg.message,
                "attachment": msg.attachment,
                "created_at": msg.created_at,
                "sender_type": sender_type,
                "sender_name": msg.sender.get_full_name() or msg.sender.phone_number,
            })

        context["messages_ordered"] = message_list
        return context
