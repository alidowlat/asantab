from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView
from accounts.models import Provider
from orders.models import Order, OrderItem, VendorOrder
from orders.services import OrderCalculator
from orders.models import STATUS_CHOICES
from wallet.models import WalletTransaction


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/main.html'
    model = Order

    def get_orders(self, is_paid, select_fields=None, status=None):
        qs = Order.objects.filter(user=self.request.user, is_paid=is_paid)
        if status:
            qs = qs.filter(status=status)
        if select_fields:
            qs = qs.prefetch_related(
                Prefetch('items', queryset=OrderItem.objects.select_related(*select_fields))
            )
        else:
            qs = qs.prefetch_related('items')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_items = self.get_orders(False, ['service', 'option', 'schedule']).order_by('-created_at')
        order_items = self.get_orders(True, ['service']).order_by('-paid_at')

        for order in order_items:
            order.calculated_final_price = OrderCalculator(order).final_price()

        context.update({
            "cart_items": cart_items,
            "order_items": order_items,
            "pending_orders": order_items.filter(status="pending"),
            "accepted_orders": order_items.filter(status="accepted"),
            "completed_orders": order_items.filter(status="completed"),
            "rejected_orders": order_items.filter(status="rejected"),
        })

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = self.get_orders(True, ['service'], status_value)

        return context


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/order/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs.get('pk')

        order = (
            Order.objects
            .filter(pk=order_pk, user=self.request.user, is_paid=True)
            .prefetch_related(
                Prefetch(
                    'vendor_orders',
                    queryset=VendorOrder.objects.prefetch_related(
                        Prefetch(
                            'items',
                            queryset=OrderItem.objects.select_related('service', 'option', 'schedule')
                        )
                    )
                )
            )
            .first()
        )

        if not order:
            raise Http404("سفارشی برای شما پیدا نشد.")

        calc = OrderCalculator(order)

        context['loaded_order'] = order
        context['vendor_orders'] = order.vendor_orders.all()
        context['discount_amount'] = calc.discount_amount()
        context['final_price'] = calc.final_price()
        return context


class ProviderOrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/provider/main.html'
    model = VendorOrder
    context_object_name = 'vendor_orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def get_vendor_orders(status=None):
            provider = get_object_or_404(Provider, user=self.request.user)
            queryset = VendorOrder.objects.filter(provider=provider)
            if status:
                queryset = queryset.filter(status=status)
            queryset = queryset.prefetch_related(
                Prefetch('items', queryset=OrderItem.objects.select_related('service'))
            )
            return queryset

        vendor_orders = get_vendor_orders()

        context['vendor_orders'] = vendor_orders

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = get_vendor_orders(status_value)

        context['final_price'] = sum(vendor_order.total_price for vendor_order in vendor_orders)

        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        provider = get_object_or_404(Provider, user=user)

        if not user.is_provider or not provider:
            return HttpResponseForbidden("شما دسترسی به این بخش ندارید.")

        if not provider.is_profile_complete and provider.status == 'active':
            messages.warning(request, "برای مشاهده سفارش‌ها، لطفاً اطلاعات حساب خود را کامل کنید.")
            return redirect('dashboard_page')

        return super().dispatch(request, *args, **kwargs)


class ProviderOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/order/provider/order_detail.html'
    model = VendorOrder
    context_object_name = 'vendor_order'

    def get_queryset(self):
        provider = get_object_or_404(Provider, user=self.request.user)
        return (
            VendorOrder.objects
            .filter(provider=provider)
            .select_related('order', 'provider')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('service', 'option', 'schedule')
                )
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "complete":
            self.object.status = "completed"
            self.object.save(update_fields=["status"])

        return redirect("received_order_detail", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor_order"] = self.object
        return context


def handle_vendor_order_response(vendor_order, accepted: bool, rejection_reason: str = None):
    order = vendor_order.order
    buyer_wallet = order.user.wallet
    seller_wallet = vendor_order.provider.user.wallet

    with transaction.atomic():
        if accepted:
            buyer_wallet.balance -= vendor_order.total_price
            buyer_wallet.frozen_balance -= vendor_order.total_price
            buyer_wallet.save(update_fields=['balance', 'frozen_balance'])

            WalletTransaction.objects.create(
                wallet=buyer_wallet,
                amount=vendor_order.total_price,
                type='transfer',
                description=f"سفارش {order.tracking_code} - انتقال به فروشنده"
            )

            WalletTransaction.objects.create(
                wallet=seller_wallet,
                amount=vendor_order.total_price,
                type='deposit',
                description=f"سفارش {order.tracking_code} - واریز به فروشنده"
            )

            seller_wallet.balance += vendor_order.total_price
            seller_wallet.save(update_fields=['balance'])

            vendor_order.status = 'accepted'
            vendor_order.rejection_reason = None
            vendor_order.save(update_fields=['status', 'rejection_reason'])

            return {"status": "success", "message": "سفارش تایید شد و مبلغ منتقل گردید."}

        else:
            buyer_wallet.frozen_balance -= vendor_order.total_price
            buyer_wallet.balance += vendor_order.total_price
            buyer_wallet.save(update_fields=['balance', 'frozen_balance'])

            WalletTransaction.objects.create(
                wallet=buyer_wallet,
                amount=vendor_order.total_price,
                type='release',
                description=f"سفارش {order.tracking_code} - رد شد، مبلغ آزاد گردید"
            )

            vendor_order.status = 'rejected'
            vendor_order.rejection_reason = rejection_reason
            vendor_order.save(update_fields=['status', 'rejection_reason'])

            return {"status": "warning", "message": "سفارش رد شد و مبلغ آزاد گردید."}


@require_POST
def vendor_order_action(request, pk, action):
    vendor_order = get_object_or_404(VendorOrder, pk=pk, provider__user=request.user)

    if action == "accept":
        data = handle_vendor_order_response(vendor_order, accepted=True)

    elif action == "reject":
        reason = request.POST.get("rejection_reason", "").strip()
        if not reason:
            return JsonResponse({"status": "error", "message": "لطفاً دلیل رد سفارش را وارد کنید."})
        data = handle_vendor_order_response(vendor_order, accepted=False, rejection_reason=reason)

    else:
        data = {"status": "error", "message": "عملیات نامعتبر است."}

    return JsonResponse(data)
