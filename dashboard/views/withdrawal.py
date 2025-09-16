from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from wallet.models import WithdrawalRequest, WalletTransaction


class WithdrawalRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/withdrawal/main.html'
    model = WithdrawalRequest
    context_object_name = 'withdrawals'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def get_withdrawals(status=None):
            queryset = WithdrawalRequest.objects.all().select_related("wallet__user", "bank_account")
            if status:
                queryset = queryset.filter(status=status)
            return queryset

        context['withdrawals'] = get_withdrawals()

        for status_value, _ in WithdrawalRequest.STATUS_CHOICES:
            context[f'{status_value}_withdrawals'] = get_withdrawals(status_value)

        return context


class WithdrawalRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = WithdrawalRequest
    template_name = "dashboard/withdrawal/detail.html"
    context_object_name = "withdrawal"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name__in='boss').exists()

    def get_queryset(self):
        return WithdrawalRequest.objects.select_related("wallet__user", "bank_account")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "complete":
            self.object.status = "paid"
            self.object.save(update_fields=["status"])

        return redirect("admin_withdrawal_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["withdrawal"] = self.object
        return context


def handle_withdrawal_response(request_obj, accepted: bool, rejection_reason: str = None):
    wallet = request_obj.wallet

    with transaction.atomic():
        if accepted:
            wallet.frozen_balance -= request_obj.amount
            wallet.save(update_fields=['frozen_balance'])

            WalletTransaction.objects.create(
                wallet=wallet,
                amount=request_obj.amount,
                type='withdraw',
                description=f"برداشت به حساب {request_obj.bank_account.card_number}"
            )

            request_obj.status = "approved"
            request_obj.rejection_reason = None
            request_obj.save(update_fields=["status", "rejection_reason"])

            return {"status": "success", "message": "برداشت تایید و پرداخت شد."}

        else:
            wallet.frozen_balance -= request_obj.amount
            wallet.balance += request_obj.amount
            wallet.save(update_fields=['balance', 'frozen_balance'])

            WalletTransaction.objects.create(
                wallet=wallet,
                amount=request_obj.amount,
                type='release',
                description=f"درخواست برداشت رد شد، مبلغ آزاد شد"
            )

            request_obj.status = "rejected"
            request_obj.rejection_reason = rejection_reason
            request_obj.save(update_fields=["status", "rejection_reason"])

            return {"status": "warning", "message": "درخواست رد شد و مبلغ آزاد گردید."}


@require_POST
def withdrawal_action(request, pk, action):
    withdrawal = get_object_or_404(WithdrawalRequest, pk=pk)

    if not request.user.is_superuser:
        return JsonResponse({"status": "error", "message": "دسترسی غیرمجاز."})

    if action == "approved":
        data = handle_withdrawal_response(withdrawal, accepted=True)

    elif action == "rejected":
        reason = request.POST.get("rejection_reason", "").strip()
        if not reason:
            return JsonResponse({"status": "error", "message": "لطفاً دلیل رد را وارد کنید."})
        data = handle_withdrawal_response(withdrawal, accepted=False, rejection_reason=reason)

    else:
        data = {"status": "error", "message": "عملیات نامعتبر است."}

    return JsonResponse(data)
