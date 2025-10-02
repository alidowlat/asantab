from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.shortcuts import redirect, render
from tickets.forms import TicketForm, TicketMessageForm


class UserTicketCreateView(LoginRequiredMixin, View):
    template_name = "tickets/user/create.html"

    def get(self, request):
        ticket_form = TicketForm()
        message_form = TicketMessageForm()
        return render(request, self.template_name, {
            "ticket_form": ticket_form,
            "message_form": message_form
        })

    def post(self, request):
        ticket_form = TicketForm(request.POST)
        message_form = TicketMessageForm(request.POST, request.FILES)

        if ticket_form.is_valid() and message_form.is_valid():
            subject = ticket_form.cleaned_data.get("subject")
            department = ticket_form.cleaned_data.get("department")
            message = message_form.cleaned_data.get("message")
            attachment = message_form.cleaned_data.get("attachment")

            if not subject or not department:
                return JsonResponse({
                    "status": "error",
                    "message": "وارد کردن موضوع و دپارتمان الزامی است."
                })

            if not message and not attachment:
                return JsonResponse({
                    "status": "error",
                    "message": "باید متن پیام یا فایل پیوست وارد شود."
                })

            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            message = message_form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "success",
                    "message": "تیکت با موفقیت ثبت شد.",
                    "redirect_url": reverse("user_ticket_detail", kwargs={"pk": ticket.pk})
                })
            return redirect("user_ticket_detail", pk=ticket.pk)

        errors = {}
        for f in [ticket_form, message_form]:
            for field, field_errors in f.errors.items():
                errors[field] = field_errors[0]

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "status": "error",
                "message": "فرم ناقص است. لطفاً فیلدهای مورد نیاز را پر کنید.",
                "errors": errors
            })

        return render(request, self.template_name, {
            "ticket_form": ticket_form,
            "message_form": message_form
        })