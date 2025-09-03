import random
import string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from wallet.forms import DepositForm
from wallet.models import DepositRequest
from wallet.services import DepositService


class DepositView(LoginRequiredMixin, FormView):
    template_name = "wallet/deposit.html"
    form_class = DepositForm
    success_url = reverse_lazy("deposit_verify")

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        deposit = DepositService.create_deposit(self.request.user, amount)
        redirect_url = DepositService.start_payment(deposit)
        if redirect_url:
            return redirect(redirect_url)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = self.request.user.wallet
        context["preset_amounts"] = [100000, 250000, 500000, 1000000]
        return context


class DepositResultView(TemplateView):
    template_name = "wallet/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ref_id = self.kwargs.get("ref_id")
        try:
            deposit = DepositRequest.objects.get(ref_id=ref_id, wallet__user=self.request.user)
        except DepositRequest.DoesNotExist:
            raise Http404("تراکنشی پیدا نشد!")

        context["deposit"] = deposit
        context["is_success"] = deposit.status == "paid"
        context["message"] = "پرداخت با موفقیت انجام شد!" if deposit.status == "paid" else "پرداخت ناموفق بود!"
        return context


@csrf_exempt
def deposit_verify(request):
    if request.method == "POST":
        transid = request.POST.get("transid")
        invoice_id = request.POST.get("invoice_id")

        try:
            deposit = DepositRequest.objects.get(id=invoice_id)
        except DepositRequest.DoesNotExist:
            return HttpResponse("Deposit not found", status=404)

        if DepositService.verify_payment(transid, deposit.amount):
            tracking_code = "".join(random.choices(string.digits, k=10))
            deposit.mark_as_paid(ref_id=transid, tracking_code=tracking_code)
        else:
            deposit.mark_failed(ref_id=transid)

        if deposit.status in ["paid", "failed"]:
            return redirect("deposit_result_view", ref_id=deposit.ref_id)

        return HttpResponse("Transaction not valid for result page", status=404)

    return HttpResponse("Invalid request", status=400)