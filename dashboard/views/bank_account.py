from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, ListView
from accounts.models import BankAccount
from dashboard.forms import BankAccountForm


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = "dashboard/bank_account/main.html"
    context_object_name = "accounts"

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user).order_by("-created_at")


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "dashboard/bank_account/create.html"
    success_url = reverse_lazy("bank_accounts_view")

    def form_valid(self, form):
        bank_account = form.save(commit=False)
        bank_account.user = self.request.user
        bank_account.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "message": "حساب بانکی با موفقیت ذخیره شد",
                "redirect_url": str(self.success_url)
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)


class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "dashboard/bank_account/edit.html"
    success_url = reverse_lazy("bank_accounts_view")

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def form_valid(self, form):
        bank_account = form.save()
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "message": "حساب بانکی با موفقیت ذخیره شد",
                "redirect_url": str(self.success_url)
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)


@login_required
def dashboard_bank_accounts_partial(request):
    accounts = BankAccount.objects.filter(user=request.user).order_by("-created_at")
    return render(request, 'dashboard/bank_account/list.html', {'accounts': accounts})


@require_POST
@login_required
def delete_bank_account(request):
    account_id = request.POST.get("id")
    try:
        account = BankAccount.objects.get(id=account_id, user=request.user)
        account.delete()
        return JsonResponse({'status': 'ok'})
    except BankAccount.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'حساب بانکی یافت نشد'})
