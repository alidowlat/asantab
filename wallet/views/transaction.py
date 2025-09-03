from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView
from wallet.models import WalletTransaction


class RecentTransactionsView(LoginRequiredMixin, ListView):
    model = WalletTransaction
    template_name = "wallet/transactions/main.html"
    context_object_name = "transactions"
    paginate_by = 10

    def get_queryset(self):
        return (
            WalletTransaction.objects
            .filter(wallet__user=self.request.user)
            .select_related("wallet", "related_wallet")
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
