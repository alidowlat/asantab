from django.db import transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from wallet.forms import WithdrawalForm
from wallet.models import WithdrawalRequest


class WithdrawView(LoginRequiredMixin, FormView):
    template_name = "wallet/withdraw/main.html"
    form_class = WithdrawalForm
    success_url = reverse_lazy("withdraw_result_view")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        bank_account = form.cleaned_data["bank_account"]
        wallet = self.request.user.wallet

        if wallet.balance < amount or wallet.balance <= 0:
            return JsonResponse({
                "success": False,
                "message": "موجودی کیف پول شما کافی نیست."
            })

        with transaction.atomic():
            wallet.balance -= amount
            wallet.frozen_balance += amount
            wallet.save()

            WithdrawalRequest.objects.create(
                wallet=wallet,
                amount=amount,
                bank_account=bank_account,
                status="pending",
                description="درخواست برداشت در حال بررسی است.",
            )

        return JsonResponse({
            "success": True,
            "message": "درخواست برداشت شما با موفقیت ثبت شد."
        })

    def form_invalid(self, form):
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(error)

        return JsonResponse({
            "success": False,
            "message": "<br><br>".join(errors) if errors else "اطلاعات فرم معتبر نیست."
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = self.request.user.wallet
        context["preset_amounts"] = [100000, 250000, 500000, 1000000]
        context["recent_withdrawals"] = WithdrawalRequest.objects.filter(wallet=self.request.user.wallet).order_by("-created_at")[:5]
        return context


class WithdrawListView(LoginRequiredMixin, ListView):
    model = WithdrawalRequest
    template_name = "wallet/withdraw/history.html"
    context_object_name = "recent_withdrawals"
    paginate_by = 10

    def get_queryset(self):
        return (
            WithdrawalRequest.objects
            .filter(wallet__user=self.request.user)
            .select_related("wallet", "bank_account")
            .order_by("-created_at")
        )

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                self.template_name,
                context,
                request=self.request
            )
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)
