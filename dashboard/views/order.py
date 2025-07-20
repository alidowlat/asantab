from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from accounts.models import Provider
from orders.models import Order, OrderItem
from orders.services import OrderCalculator
from orders.models import STATUS_CHOICES


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/main.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)

        def get_orders(is_paid, select_fields=None, status=None):
            queryset = Order.objects.filter(user=self.request.user, is_paid=is_paid)
            if status:
                queryset = queryset.filter(status=status)
            if select_fields:
                queryset = queryset.prefetch_related(
                    Prefetch('items', queryset=OrderItem.objects.select_related(*select_fields))
                )
            else:
                queryset = queryset.prefetch_related('items')
            return queryset

        cart_items = get_orders(False, ['service', 'option', 'schedule'])
        order_items = get_orders(True, ['service'])

        context['cart_items'] = cart_items
        context['order_items'] = order_items

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = get_orders(True, ['service'], status_value)

        context['final_price'] = sum(OrderCalculator(order).final_price() for order in order_items)

        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/order/order_detail.html'
    model = Order

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_paid=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        calc = OrderCalculator(order)

        context['discount_amount'] = calc.discount_amount()
        context['loaded_order'] = order
        context['final_price'] = calc.final_price()
        return context


class ProviderOrderListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/order/provider/main.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(ProviderOrderListView, self).get_context_data(**kwargs)

        def get_orders(is_paid, select_fields=None, status=None):
            provider = get_object_or_404(Provider, user=self.request.user)
            queryset = Order.objects.filter(provider=provider, is_paid=is_paid)
            if status:
                queryset = queryset.filter(status=status)
            if select_fields:
                queryset = queryset.prefetch_related(
                    Prefetch('items', queryset=OrderItem.objects.select_related(*select_fields))
                )
            else:
                queryset = queryset.prefetch_related('items')
            return queryset

        order_items = get_orders(True, ['service'])

        context['order_items'] = order_items

        for status_value, _ in STATUS_CHOICES:
            context[f'order_{status_value}'] = get_orders(True, ['service'], status_value)

        context['final_price'] = sum(OrderCalculator(order).final_price() for order in order_items)

        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        provider = get_object_or_404(Provider, user=user)

        if not user.is_provider or not provider:
            return HttpResponseForbidden("شما دسترسی به این بخش ندارید.")

        if not provider.is_profile_complete:
            messages.warning(request, "برای مشاهده سفارش‌ها، لطفاً اطلاعات حساب خود را کامل کنید.")
            return redirect('dashboard_page')

        return super().dispatch(request, *args, **kwargs)


class ProviderOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/order/provider/order_detail.html'
    model = Order

    def get_queryset(self):
        return Order.objects.filter(provider_id=self.request.user.id, is_paid=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        calc = OrderCalculator(order)

        context['discount_amount'] = calc.discount_amount()
        context['loaded_order'] = order
        context['final_price'] = calc.final_price()
        return context