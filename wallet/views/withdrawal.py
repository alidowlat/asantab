from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from wallet.forms import WithdrawalForm
from wallet.models import WithdrawalRequest
from wallet.services import WithdrawService


class WithdrawView(LoginRequiredMixin, FormView):
    template_name = "wallet/withdraw.html"
    form_class = WithdrawalForm
    success_url = reverse_lazy("withdraw_result_view")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        bank_account = form.cleaned_data["bank_account"]

        withdraw = WithdrawService.create_withdraw(self.request.user, amount, bank_account)
        result = WithdrawService.start_withdraw(withdraw)
        if result:
            return redirect("withdraw_result_view", pk=withdraw.pk)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = self.request.user.wallet
        context["preset_amounts"] = [100000, 250000, 500000, 1000000]
        return context


class WithdrawResultView(LoginRequiredMixin, TemplateView):
    template_name = "wallet/withdraw_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            withdraw = WithdrawalRequest.objects.get(pk=self.kwargs["pk"], wallet__user=self.request.user)
        except WithdrawalRequest.DoesNotExist:
            raise Http404("درخواست برداشت پیدا نشد!")

        context["withdraw"] = withdraw
        context["is_success"] = withdraw.status == "paid"
        if withdraw.status == "paid":
            context["message"] = "برداشت با موفقیت ثبت شد!"
        elif withdraw.status == "rejected":
            context["message"] = "برداشت توسط سیستم رد شد!"
        else:
            context["message"] = "برداشت ناموفق بود!"

        return context


@csrf_exempt
def withdrawal_verify(request):
    if request.method == "POST":
        transid = request.POST.get("transid")
        withdrawal_id = request.POST.get("withdrawal_id")

        try:
            withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id)
        except WithdrawalRequest.DoesNotExist:
            return HttpResponse("Withdrawal not found", status=404)

        if WithdrawService.verify_withdraw(transid, withdrawal.amount):
            withdrawal.mark_as_paid(reference_id=transid)
        else:
            withdrawal.mark_rejected()

        if withdrawal.status in ["paid", "rejected"]:
            return redirect("withdrawal_result_view", pk=withdrawal.id)

        return HttpResponse("Transaction not valid for result page", status=404)

    return HttpResponse("Invalid request", status=400)
