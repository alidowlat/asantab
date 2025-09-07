from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from wallet.models import Wallet, WalletTransaction


class WalletView(LoginRequiredMixin, TemplateView):
    template_name = "wallet/main.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        ctx["wallet"] = wallet

        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]
        ctx["transactions"] = transactions

        return ctx
